/**
 * Name: vertical_flow
 * Non-spatial vertical-movement generator with ground-truth logging (spec §4.2) and a
 * virtual one-person observer (spec §4.3). Inputs: the key-value cell file written by
 * analysis/R/gama_runner.R::write_cell(). Outputs: CSV contracts in analysis/R/io.R.
 * Spec: docs/superpowers/specs/2026-10-20-simulation-track-design.md; ODD: docs/simulation/ODD.md
 *
 * GAMA 2025.06.4 idioms (see simulation/README.md): gama.machine_time, not machine_time; GAML
 * ranges count down, so every loop whose range can be empty is guarded; strings written with
 * save ... format: "csv" are not quoted, so they must not contain commas, quotes or newlines.
 */
model vertical_flow

global {
	// ---- run identity (headless XML parameters) ----
	string cell_file <- "";
	int rep_id <- 0;
	bool show_view <- false;
	float step <- 10.0 #s;

	// ---- configuration ----
	map<string, string> kv <- [];
	string cell_id <- "";
	string out_dir <- "";
	int n_floors <- 0;
	int n_bnd <- 0;
	list<string> floor_code <- [];
	list<float> ln_size <- [];
	list<float> x_fnb <- [];
	list<float> dwell_offset <- [];
	list<bool> elev_served <- [];
	list<string> boundary_id <- [];
	list<int> boundary_order <- [];
	list<bool> esc_up <- [];
	list<bool> esc_down <- [];
	list<bool> stair_ok <- [];
	list<int> entry_floor_idx <- [];
	list<float> entry_share <- [];
	list<string> block_id <- [];
	list<float> block_start_s <- [];
	list<float> block_end_s <- [];
	list<float> prof_wd <- list_with(24, 0.0);
	list<float> prof_we <- list_with(24, 0.0);
	float open_s <- 0.0;
	float day_len_s <- 0.0;
	int n_days <- 1;
	list<string> day_types <- [];

	// ---- behavioural parameters (spec §4.2) ----
	float p_alpha <- 0.0;
	float p_beta <- 0.0;
	float p_gamma <- 0.0;
	float p_delta_down <- 0.0;
	float p_theta0 <- 0.0;
	float p_theta1 <- 0.0;
	float p_theta2 <- 0.0;
	list<float> imp <- [1.0, 1.0, 1.0];
	list<float> tau <- [0.0, 0.0, 0.0];
	float mode_mu <- 1.0;
	bool elevator_enabled <- true;
	float base_rate_gpm <- 0.0;
	float group_extra_mean <- 0.0;
	float day_sd <- 0.0;
	float dwell_meanlog <- 0.0;
	float dwell_sdlog <- 0.0;
	float esc_s <- 45.0;
	float stair_s <- 60.0;
	float elev_wait_mean_s <- 60.0;
	float elev_s_per_floor <- 6.0;
	bool log_crossings <- false;
	bool log_decisions <- false;
	bool observers_enabled <- false;
	bool x_fnb_random <- false;

	// ---- precomputed choice structure, flattened as i * n_floors + j ----
	list<float> u_dest <- [];
	list<bool> dest_ok <- [];
	list<float> mode_p <- [];

	// ---- day state ----
	int cur_day <- 1;
	bool running_day <- true;
	float day_start_t <- 0.0;
	float day_mult <- 1.0;
	int next_gid <- 0;
	int groups_entered <- 0;
	int persons_entered <- 0;
	int persons_exited <- 0;
	list<int> truth_acc <- [];
	list<list> crossing_rows <- [];
	list<list> decision_rows <- [];
	float wall_t0 <- 0.0;

	list<string> MODE_NAME <- ["escalator", "stairs", "elevator"];
	list<string> DIR_NAME <- ["up", "down"];

	init {
		wall_t0 <- gama.machine_time;
		do load_kv;
		do load_parameters;
		do load_floors(file_name: kv["floors_file"]);
		do load_boundaries(file_name: kv["boundaries_file"]);
		do load_entries(file_name: kv["entries_file"]);
		do load_blocks(file_name: kv["blocks_file"]);
		do load_profile(file_name: kv["day_profile_file"]);
		do load_facility(file_name: kv["facility_file"]);
		if (n_floors < 2) { error "the facility needs at least two floors"; }
		if (n_days < 1) { error "n_days must be at least 1"; }
		if (length(entry_share) < 1) { error "entries.csv has no rows"; }
		if (length(block_id) < 1) { error "blocks.csv has no rows"; }
		do write_headers;
		if (x_fnb_random) { do draw_program; }
		do precompute;
		truth_acc <- list_with(length(block_id) * n_bnd * 6, 0);
		if (observers_enabled) { do load_observers; }
		do start_day;
	}

	float pf (string k) {
		if (!(kv contains_key k)) {
			error "cell file " + cell_file + " is missing key " + k;
		}
		return float(kv[k]);
	}

	action load_kv {
		matrix m <- matrix(csv_file(cell_file, ",", true));
		if (m.rows > 0) {
			loop r from: 0 to: m.rows - 1 {
				kv[string(m[0, r])] <- string(m[1, r]);
			}
		}
	}

	action load_parameters {
		cell_id <- kv["cell_id"];
		out_dir <- kv["out_root"] + "/rep_" + string(rep_id);
		n_days <- int(pf("n_days"));
		day_types <- kv["day_types"] split_with ";";
		if (length(day_types) != n_days) { error "day_types must list one day type per simulated day"; }
		p_alpha <- pf("alpha");
		p_beta <- pf("beta");
		p_gamma <- pf("gamma");
		p_delta_down <- pf("delta_down");
		p_theta0 <- pf("theta0");
		p_theta1 <- pf("theta1");
		p_theta2 <- pf("theta2");
		imp <- [pf("imp_escalator"), pf("imp_stairs"), pf("imp_elevator")];
		tau <- [pf("tau_escalator"), pf("tau_stairs"), pf("tau_elevator")];
		mode_mu <- pf("mode_mu");
		elevator_enabled <- pf("elevator_enabled") = 1.0;
		base_rate_gpm <- pf("base_rate_gpm");
		group_extra_mean <- pf("group_extra_mean");
		day_sd <- pf("day_sd");
		dwell_meanlog <- pf("dwell_meanlog");
		dwell_sdlog <- pf("dwell_sdlog");
		esc_s <- pf("esc_s");
		stair_s <- pf("stair_s");
		elev_wait_mean_s <- pf("elev_wait_mean_s");
		elev_s_per_floor <- pf("elev_s_per_floor");
		log_crossings <- pf("log_crossings") = 1.0;
		log_decisions <- pf("log_decisions") = 1.0;
		observers_enabled <- pf("observers_enabled") = 1.0;
		x_fnb_random <- pf("x_fnb_random") = 1.0;
		day_len_s <- pf("sim_end_min") * 60.0;  // load_facility subtracts the opening time
	}

	action load_floors (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		n_floors <- m.rows;
		if (n_floors > 0) {
			loop r from: 0 to: n_floors - 1 {
				if (int(m[1, r]) != r) { error "floors.csv must be sorted by floor_index starting at 0"; }
				floor_code <+ string(m[0, r]);
				ln_size <+ ln(float(m[2, r]));
				x_fnb <+ float(m[3, r]);
				dwell_offset <+ float(m[4, r]);
				elev_served <+ (int(m[5, r]) = 1);
			}
		}
	}

	action load_boundaries (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		n_bnd <- m.rows;
		if (n_bnd != n_floors - 1) { error "boundaries.csv needs one row per consecutive floor pair"; }
		if (n_bnd > 0) {
			loop r from: 0 to: n_bnd - 1 {
				boundary_id <+ string(m[1, r]);
				boundary_order <+ int(m[4, r]);
				esc_up <+ (int(m[5, r]) = 1);
				esc_down <+ (int(m[6, r]) = 1);
				stair_ok <+ (int(m[7, r]) = 1);
			}
		}
	}

	action load_entries (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		if (m.rows > 0) {
			loop r from: 0 to: m.rows - 1 {
				entry_floor_idx <+ int(m[1, r]);
				entry_share <+ float(m[3, r]);
			}
		}
	}

	action load_blocks (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		if (m.rows > 0) {
			loop r from: 0 to: m.rows - 1 {
				block_id <+ string(m[0, r]);
				block_start_s <+ float(m[1, r]) * 60.0;
				block_end_s <+ float(m[2, r]) * 60.0;
			}
		}
	}

	action load_profile (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		if (m.rows > 0) {
			loop r from: 0 to: m.rows - 1 {
				int h <- int(m[0, r]);
				prof_wd[h] <- float(m[1, r]);
				prof_we[h] <- float(m[2, r]);
			}
		}
	}

	action load_facility (string file_name) {
		matrix m <- matrix(csv_file(file_name, ",", true));
		if (m.rows > 0) {
			loop r from: 0 to: m.rows - 1 {
				if (string(m[0, r]) = "open_min") { open_s <- float(m[1, r]) * 60.0; }
			}
		}
		day_len_s <- day_len_s - open_s;
		if (day_len_s <= 0.0) { error "sim_end_min must be later than open_min"; }
	}

	// One observer agent per protocol. The schedule CSV is sorted by protocol, day,
	// boundary_index and start (schedule_for_gama), so each (day, boundary) segment is contiguous.
	// Both row loops are guarded: GAML ranges count down, so an empty table would loop twice.
	action load_observers {
		matrix pm <- matrix(csv_file(kv["protocols_file"], ",", true));
		matrix sm <- matrix(csv_file(kv["schedule_file"], ",", true));
		if (pm.rows > 0) {
			loop r from: 0 to: pm.rows - 1 {
				string pid <- string(pm[0, r]);
				create field_observer {
					protocol_id <- pid;
					construct_label <- string(pm[1, r]);
					list<string> cm <- string(pm[2, r]) split_with ";";
					count_mode <- [cm contains "escalator", cm contains "stairs", cm contains "elevator"];
					count_down <- int(pm[3, r]) = 1;
					miss_base <- float(pm[4, r]);
					miss_edge <- float(pm[5, r]);
					miss_edge_s <- float(pm[6, r]);
					miss_flow <- float(pm[7, r]);
					down_load <- float(pm[8, r]);
					seg_start <- list_with(n_days * n_bnd, 0);
					seg_len <- list_with(n_days * n_bnd, 0);
					if (sm.rows > 0) {
						loop s from: 0 to: sm.rows - 1 {
							if (string(sm[0, s]) = pid) {
								int dd <- int(sm[1, s]);
								int bi <- int(sm[5, s]);
								int sk <- (dd - 1) * n_bnd + bi;
								if (seg_len[sk] = 0) { seg_start[sk] <- length(w_id); }
								seg_len[sk] <- seg_len[sk] + 1;
								w_day <+ dd;
								w_block <+ string(sm[2, s]);
								w_id <+ string(sm[3, s]);
								w_b <+ bi;
								w_order <+ int(sm[6, s]);
								w_start <+ float(sm[7, s]);
								w_end <+ float(sm[8, s]);
								w_up <+ 0;
								w_down <+ (count_down ? 0 : -1);
								w_true_up <+ 0;
								w_true_down <+ 0;
							}
						}
					}
					ptr <- copy(seg_start);
				}
			}
		}
	}

	action write_headers {
		save ["cell_id", "rep_id", "day", "day_type", "block_id", "boundary_id", "direction", "mode", "persons"]
			to: out_dir + "/truth.csv" format: "csv" rewrite: true header: false;
		save ["cell_id", "rep_id", "day", "groups_entered", "persons_entered", "persons_exited", "persons_forced_exit"]
			to: out_dir + "/conservation.csv" format: "csv" rewrite: true header: false;
		save ["cell_id", "rep_id", "day", "wall_ms"]
			to: out_dir + "/timing.csv" format: "csv" rewrite: true header: false;
		if (log_crossings) {
			save ["cell_id", "rep_id", "day", "group_id", "trip_no", "time_s", "boundary_id", "direction", "mode", "persons"]
				to: out_dir + "/crossings.csv" format: "csv" rewrite: true header: false;
		}
		if (log_decisions) {
			save ["cell_id", "rep_id", "day", "group_id", "trip_no", "time_s", "origin_index", "elapsed_min", "choice_index", "dest_index", "mode_index"]
				to: out_dir + "/decisions.csv" format: "csv" rewrite: true header: false;
		}
		if (x_fnb_random) {
			save ["cell_id", "rep_id", "floor_index", "x_fnb"]
				to: out_dir + "/floors_realized.csv" format: "csv" rewrite: true header: false;
		}
		if (observers_enabled) {
			save ["cell_id", "rep_id", "protocol_id", "day", "day_type", "block_id", "window_id", "boundary_id",
				"boundary_order", "observation_order", "window_start_s", "window_end_s", "window_minutes",
				"construct_label", "up_count", "down_count", "true_up_window", "true_down_window", "valid_window"]
				to: out_dir + "/observed.csv" format: "csv" rewrite: true header: false;
		}
	}

	// A5 only: floor program drawn per replicate (spec §5 A5).
	action draw_program {
		float lo <- pf("x_fnb_low");
		float hi <- pf("x_fnb_high");
		if (n_floors > 0) {
			loop f from: 0 to: n_floors - 1 {
				x_fnb[f] <- lo + rnd(hi - lo);
				save [cell_id, rep_id, f, x_fnb[f]] to: out_dir + "/floors_realized.csv" format: "csv" rewrite: false header: false;
			}
		}
	}

	bool mode_available (int i, int j, int m) {
		if (m = 2) { return elevator_enabled and elev_served[i] and elev_served[j]; }
		int lo <- min([i, j]);
		int hi <- max([i, j]) - 1;
		bool ok <- true;
		if (hi >= lo) {
			loop b from: lo to: hi {
				if (m = 1 and !stair_ok[b]) { ok <- false; }
				if (m = 0 and j > i and !esc_up[b]) { ok <- false; }
				if (m = 0 and j < i and !esc_down[b]) { ok <- false; }
			}
		}
		return ok;
	}

	// Nested logit: lower-level mode probabilities and composite impedance (spec §4.2).
	action precompute {
		u_dest <- list_with(n_floors * n_floors, -1.0e9);
		dest_ok <- list_with(n_floors * n_floors, false);
		mode_p <- list_with(n_floors * n_floors * 3, 0.0);
		if (n_floors > 0) {
			loop i from: 0 to: n_floors - 1 {
				loop j from: 0 to: n_floors - 1 {
					if (i != j) {
						int d <- abs(j - i);
						list<float> c <- [0.0, 0.0, 0.0];
						list<bool> ok <- [mode_available(i, j, 0), mode_available(i, j, 1), mode_available(i, j, 2)];
						float s <- 0.0;
						loop m from: 0 to: 2 {
							if (ok[m]) {
								c[m] <- ln(imp[m]) + tau[m] * (d - 1);
								s <- s + exp(-mode_mu * c[m]);
							}
						}
						if (s > 0.0) {
							float ln_ibar <- -ln(s) / mode_mu;
							loop m from: 0 to: 2 {
								if (ok[m]) { mode_p[(i * n_floors + j) * 3 + m] <- exp(-mode_mu * c[m]) / s; }
							}
							dest_ok[i * n_floors + j] <- true;
							u_dest[i * n_floors + j] <- ln_size[j] + p_gamma * x_fnb[j] - p_alpha * ln(float(d))
								- p_beta * ln_ibar + ((j < i) ? p_delta_down : 0.0);
						}
					}
				}
			}
		}
	}

	action start_day {
		day_start_t <- time;
		day_mult <- exp(gauss(-0.5 * day_sd * day_sd, day_sd));
		groups_entered <- 0;
		persons_entered <- 0;
		persons_exited <- 0;
		truth_acc <- list_with(length(truth_acc), 0);
		crossing_rows <- [];
		decision_rows <- [];
	}

	action write_day_outputs (int forced) {
		string dtype <- day_types[cur_day - 1];
		if (length(block_id) > 0 and n_bnd > 0) {
			loop k from: 0 to: length(block_id) - 1 {
				loop b from: 0 to: n_bnd - 1 {
					loop di from: 0 to: 1 {
						loop m from: 0 to: 2 {
							save [cell_id, rep_id, cur_day, dtype, block_id[k], boundary_id[b], DIR_NAME[di], MODE_NAME[m],
								truth_acc[((k * n_bnd + b) * 2 + di) * 3 + m]]
								to: out_dir + "/truth.csv" format: "csv" rewrite: false header: false;
						}
					}
				}
			}
		}
		save [cell_id, rep_id, cur_day, groups_entered, persons_entered, persons_exited, forced]
			to: out_dir + "/conservation.csv" format: "csv" rewrite: false header: false;
		if (log_crossings and !empty(crossing_rows)) {
			loop row over: crossing_rows { save row to: out_dir + "/crossings.csv" format: "csv" rewrite: false header: false; }
		}
		if (log_decisions and !empty(decision_rows)) {
			loop row over: decision_rows { save row to: out_dir + "/decisions.csv" format: "csv" rewrite: false header: false; }
		}
		if (observers_enabled) { ask field_observer { do write_day; } }
		save [cell_id, rep_id, cur_day, gama.machine_time - wall_t0]
			to: out_dir + "/timing.csv" format: "csv" rewrite: false header: false;
	}

	action close_day {
		int forced <- sum(visitor collect each.persons);
		ask visitor { do die; }
		do write_day_outputs(forced: forced);
		if (cur_day < n_days) {
			cur_day <- cur_day + 1;
			do start_day;
		} else {
			running_day <- false;
		}
	}

	reflex end_of_day when: running_day and (time - day_start_t) >= day_len_s {
		do close_day;
	}

	reflex arrivals when: running_day {
		float tod <- open_s + (time - day_start_t);
		int h <- min([int(tod / 3600.0), 23]);
		float prof <- (day_types[cur_day - 1] = "WE") ? prof_we[h] : prof_wd[h];
		if (prof > 0.0 and length(entry_share) > 0) {
			loop e from: 0 to: length(entry_share) - 1 {
				float lam <- base_rate_gpm * entry_share[e] * prof * day_mult * step / 60.0;
				if (lam > 0.0) {
					int n <- poisson(lam);
					if (n > 0) {
						int ef <- entry_floor_idx[e];
						create visitor number: n {
							gid <- next_gid;
							next_gid <- next_gid + 1;
							persons <- 1 + poisson(group_extra_mean);
							entry_floor <- ef;
							cur_floor <- ef;
							t_enter <- time;
							next_t <- time + dwell_draw(ef);
							groups_entered <- groups_entered + 1;
							persons_entered <- persons_entered + persons;
						}
					}
				}
			}
		}
	}
}

species visitor {
	int gid <- 0;
	int persons <- 1;
	int entry_floor <- 0;
	int cur_floor <- 0;
	float t_enter <- 0.0;
	float next_t <- 0.0;
	bool moving <- false;
	bool leaving <- false;
	int dest_floor <- 0;
	int mode_m <- 0;
	int dir <- 1;
	float arrive_t <- 0.0;
	list<int> cb <- [];
	list<float> ct <- [];
	int trip_no <- 0;

	float dwell_draw (int f) {
		return 60.0 * exp(gauss(dwell_meanlog + dwell_offset[f], dwell_sdlog));
	}

	// Upper level of the nested logit: exit or a destination floor (index k = floor + 1).
	list<float> choice_probs (int i, float elapsed_min) {
		list<float> v <- list_with(n_floors + 1, 0.0);
		list<bool> ok <- list_with(n_floors + 1, false);
		v[0] <- p_theta0 + p_theta1 * elapsed_min + p_theta2 * x_fnb[i];
		ok[0] <- true;
		float vmax <- v[0];
		if (n_floors > 0) {
			loop j from: 0 to: n_floors - 1 {
				if (dest_ok[i * n_floors + j]) {
					v[j + 1] <- u_dest[i * n_floors + j];
					ok[j + 1] <- true;
					if (v[j + 1] > vmax) { vmax <- v[j + 1]; }
				}
			}
		}
		list<float> p <- list_with(n_floors + 1, 0.0);
		float s <- 0.0;
		loop k from: 0 to: n_floors {
			if (ok[k]) {
				p[k] <- exp(v[k] - vmax);
				s <- s + p[k];
			}
		}
		loop k from: 0 to: n_floors { p[k] <- p[k] / s; }
		return p;
	}

	reflex act when: time >= next_t {
		if (moving) {
			loop while: !empty(ct) {
				if (ct[0] > time) { break; }
				do cross(b: cb[0], t: ct[0]);
				remove index: 0 from: cb;
				remove index: 0 from: ct;
			}
			if (!empty(ct)) {
				next_t <- ct[0];
			} else {
				if (time >= arrive_t) { do arrive; } else { next_t <- arrive_t; }
			}
		} else {
			do decide;
		}
	}

	action decide {
		float elapsed <- (time - t_enter) / 60.0;
		int c <- rnd_choice(choice_probs(cur_floor, elapsed));
		if (c = 0) {
			leaving <- true;
			if (cur_floor = entry_floor) {
				do log_decision(elapsed: elapsed, choice: 0, dest: -1, m: -1);
				do leave;
			} else {
				do start_trip(j: entry_floor);
				do log_decision(elapsed: elapsed, choice: 0, dest: entry_floor, m: mode_m);
			}
		} else {
			do start_trip(j: c - 1);
			do log_decision(elapsed: elapsed, choice: c, dest: c - 1, m: mode_m);
		}
	}

	// Lower level: mode choice, then the sequence of boundary crossings (spec §4.2).
	action start_trip (int j) {
		int i <- cur_floor;
		int base <- (i * n_floors + j) * 3;
		int m <- rnd_choice([mode_p[base], mode_p[base + 1], mode_p[base + 2]]);
		int d <- abs(j - i);
		if (d < 1) { error "a trip must change floor"; }
		dir <- (j > i) ? 1 : -1;
		mode_m <- m;
		dest_floor <- j;
		trip_no <- trip_no + 1;
		cb <- [];
		ct <- [];
		float t0 <- time;
		if (m = 2) {
			t0 <- t0 - elev_wait_mean_s * ln(1.0 - rnd(0.999));
			loop k from: 1 to: d {
				cb <+ ((dir > 0) ? (i + k - 1) : (i - k));
				ct <+ t0 + k * elev_s_per_floor;
			}
			arrive_t <- t0 + d * elev_s_per_floor;
		} else {
			float per <- (m = 0) ? esc_s : stair_s;
			loop k from: 1 to: d {
				cb <+ ((dir > 0) ? (i + k - 1) : (i - k));
				ct <+ t0 + (k - 0.5) * per;
			}
			arrive_t <- t0 + d * per;
		}
		moving <- true;
		next_t <- ct[0];
	}

	action cross (int b, float t) {
		float tod <- open_s + (t - day_start_t);
		int di <- (dir > 0) ? 0 : 1;
		int blk <- -1;
		if (length(block_id) > 0) {
			loop k from: 0 to: length(block_id) - 1 {
				if (tod >= block_start_s[k] and tod < block_end_s[k]) { blk <- k; }
			}
		}
		if (blk >= 0) {
			int idx <- ((blk * n_bnd + b) * 2 + di) * 3 + mode_m;
			truth_acc[idx] <- truth_acc[idx] + persons;
		}
		if (log_crossings) {
			crossing_rows <+ [cell_id, rep_id, cur_day, gid, trip_no, tod, boundary_id[b], DIR_NAME[di], MODE_NAME[mode_m], persons];
		}
		if (observers_enabled) {
			int mm <- mode_m;
			int nn <- persons;
			ask field_observer { do see(b: b, di: di, m: mm, n: nn, tod: tod); }
		}
	}

	action arrive {
		moving <- false;
		cur_floor <- dest_floor;
		if (leaving and cur_floor = entry_floor) {
			do leave;
		} else {
			next_t <- time + dwell_draw(cur_floor);
		}
	}

	action leave {
		persons_exited <- persons_exited + persons;
		do die;
	}

	action log_decision (float elapsed, int choice, int dest, int m) {
		if (log_decisions) {
			decision_rows <+ [cell_id, rep_id, cur_day, gid, trip_no, open_s + (time - day_start_t), cur_floor, elapsed, choice, dest, m];
		}
	}
}

// Virtual one-person observer (spec §4.3). It counts only the declared route construct,
// with a per-person miss probability that is higher near window edges and at higher
// load, and with an extra load factor when down flow is also counted.
species field_observer {
	string protocol_id <- "";
	string construct_label <- "";
	list<bool> count_mode <- [false, false, false];
	bool count_down <- false;
	float miss_base <- 0.0;
	float miss_edge <- 0.0;
	float miss_edge_s <- 0.0;
	float miss_flow <- 0.0;
	float down_load <- 1.0;
	list<int> w_day <- [];
	list<string> w_block <- [];
	list<string> w_id <- [];
	list<int> w_b <- [];
	list<int> w_order <- [];
	list<float> w_start <- [];
	list<float> w_end <- [];
	list<int> w_up <- [];
	list<int> w_down <- [];
	list<int> w_true_up <- [];
	list<int> w_true_down <- [];
	list<int> seg_start <- [];
	list<int> seg_len <- [];
	list<int> ptr <- [];

	// Crossings arrive at most one step out of time order, so a window is skipped only
	// once it ended more than one step before the crossing being processed.
	action see (int b, int di, int m, int n, float tod) {
		if (count_mode[m]) {
			int sk <- (cur_day - 1) * n_bnd + b;
			int p <- ptr[sk];
			int seg_end <- seg_start[sk] + seg_len[sk];
			loop while: p < seg_end {
				if (w_end[p] + step < tod) { p <- p + 1; } else { break; }
			}
			ptr[sk] <- p;
			int hit <- -1;
			if (p < seg_end) {
				if (w_start[p] <= tod and tod < w_end[p]) { hit <- p; }
			}
			if (hit < 0 and p + 1 < seg_end) {
				if (w_start[p + 1] <= tod and tod < w_end[p + 1]) { hit <- p + 1; }
			}
			if (hit >= 0) { do tally(idx: hit, di: di, n: n, tod: tod); }
		}
	}

	// binomial(n, 1.0) never returns on GAMA 2025.06.4 (OutOfMemoryError), so a miss
	// probability of 0 (the perfect protocols) is handled by the ternary guard.
	action tally (int idx, int di, int n, float tod) {
		if (di = 0) { w_true_up[idx] <- w_true_up[idx] + n; } else { w_true_down[idx] <- w_true_down[idx] + n; }
		float el <- max([1.0, (tod - w_start[idx]) / 60.0]);
		bool edge <- ((tod - w_start[idx]) < miss_edge_s) or ((w_end[idx] - tod) < miss_edge_s);
		float load <- (w_true_up[idx] + (count_down ? w_true_down[idx] : 0)) / el;
		float pm <- miss_base + (edge ? miss_edge : 0.0) + miss_flow * load;
		if (count_down) { pm <- pm * down_load; }
		pm <- min([0.95, max([0.0, pm])]);
		if (di = 0) {
			w_up[idx] <- w_up[idx] + (((1.0 - pm) >= 1.0) ? n : binomial(n, 1.0 - pm));
		} else {
			if (count_down) { w_down[idx] <- w_down[idx] + (((1.0 - pm) >= 1.0) ? n : binomial(n, 1.0 - pm)); }
		}
	}

	action write_day {
		if (!empty(w_id)) {
			loop k from: 0 to: length(w_id) - 1 {
				if (w_day[k] = cur_day) {
					save [cell_id, rep_id, protocol_id, cur_day, day_types[cur_day - 1], w_block[k], w_id[k],
						boundary_id[w_b[k]], boundary_order[w_b[k]], w_order[k], w_start[k], w_end[k],
						int((w_end[k] - w_start[k]) / 60.0), construct_label, w_up[k], w_down[k],
						w_true_up[k], w_true_down[k], true]
						to: out_dir + "/observed.csv" format: "csv" rewrite: false header: false;
				}
			}
		}
	}
}

experiment headless_run type: gui {
	parameter "cell_file" var: cell_file;
	parameter "rep_id" var: rep_id;
}


/*
 * Independent visual-capture experiment.
 * Does NOT change the original headless experiment, model choices, or data.
 * Nine horizontal bands are a purely conceptual non-spatial diagram.
 * Counts derive from the actual running GAML state at each refresh.
 */
experiment visual_capture type: gui {
    parameter "cell_file" var: cell_file;
    parameter "rep_id" var: rep_id;
    output {
        display "Upward_Boundaries" type: 2d background: rgb(250,251,253) {
            graphics "boundary_telemetry" {
                draw rectangle(94.0, 95.0) at: {50.0,49.0} color: rgb(250,251,253);
                draw "GAMA 2025.06.4 — VERTICAL FLOW" at: {10.0, 4.5} size: 11 color: rgb(29,44,63);
                draw "9-floor non-spatial model | live simulator state" at: {10.0, 10.0} size: 8 color: rgb(80,96,114);
                draw ("cycle " + string(cycle) + "   |   day " + string(cur_day)) at: {10.0, 15.0} size: 8 color: rgb(80,96,114);
                draw ("entered " + string(persons_entered) + "   |   exited " + string(persons_exited))
                    at: {10.0, 20.0} size: 8 color: rgb(80,96,114);
                loop f from: 0 to: 8 {
                    float yy <- 28.0 + (8 - f) * 8.0;
                    int present <- sum(visitor where (each.cur_floor = f) collect each.persons);
                    float ww <- min([44.0, float(present) * 0.16]);
                    draw rectangle(60.0, 6.5) at: {39.0, yy} color: rgb(229,233,240);
                    if (ww > 0.0) {
                        draw rectangle(ww, 3.5) at: {12.0 + ww / 2.0, yy} color: rgb(39,117,192);
                    }
                    draw (string(f + 1) + "F") at: {3.5, yy + 0.9} size: 7 color: rgb(44,52,69);
                    draw ("n=" + string(present)) at: {58.0, yy + 0.9} size: 6 color: rgb(80,96,114);
                }
                draw "UPWARD CROSSINGS" at: {72.0, 24.0} size: 6 color: rgb(29,44,63);
                loop b from: 0 to: 7 {
                    int ub <- 0;
                    loop k from: 0 to: length(block_id) - 1 {
                        loop m from: 0 to: 2 {
                            ub <- ub + truth_acc[((k * n_bnd + b) * 2) * 3 + m];
                        }
                    }
                    float yyb <- 32.0 + (7-b) * 8.0;
                    draw ("U" + string(b+1) + ": " + string(ub)) at: {74.0, yyb} size: 6 color: rgb(25,62,98);
                }
                draw "DISPLAY: schematic aggregation; agents have no physical XY positions"
                    at: {9.0, 97.0} size: 7 color: rgb(100,100,105);
            }
        }

        /*
         * Data-driven schematic mall scene. Every occupied-floor count and
         * crossing U(b) is read from the live GAML model. Shop shells,
         * escalators and dots are explanatory graphics, not XY trajectories.
         * One blue dot represents approximately 5 people on the floor.
         */
        display "Mall_Scene" type: 2d background: rgb(248,250,253) {
            graphics "actual_state_mall_scene" {
                draw rectangle(100.0, 100.0) at: {50.0, 50.0} color: rgb(247,249,253);
                draw rectangle(100.0, 11.0) at: {50.0, 5.5} color: rgb(22,37,59);
                draw "GAMA 2025.06.4 | LIVE VERTICAL FLOW" at: {3.0,6.5} size: 9.5 color: rgb(250,252,255);
                draw ("GAMMA " + string(p_gamma) + " / TICK " + string(cycle)) at: {58.0,6.5} size: 7 color: rgb(158,211,251);
                draw "RETAIL VERTICAL SECTION" at: {9.0,14.1} size: 7 color: rgb(25,44,69);
                draw "9 synthetic floors - actual floor occupancy / conceptual layout" at: {9.0,17.7} size: 5.7 color: rgb(88,104,124);

                // Dark rear core gives the scene a sectional depth cue.
                draw rectangle(66.0, 71.0) at: {40.5,53.0} color: rgb(218,226,237);
                draw rectangle(60.0, 69.0) at: {42.5,52.5} color: rgb(244,248,251);
                // Repeated level bays, simple shopfronts and live density glyphs.
                loop f from: 0 to: 8 {
                    float yy <- 23.0 + (8 - f) * 7.35;
                    int present <- sum(visitor where (each.cur_floor = f) collect each.persons);
                    draw rectangle(59.0, 6.1) at: {42.5, yy} color: rgb(232,237,245);
                    // Glass shop bays: illustrative architectural context.
                    draw rectangle(16.2, 4.8) at: {21.5,yy} color: rgb(249,248,246);
                    draw rectangle(16.2, 4.8) at: {39.0,yy} color: rgb(246,249,252);
                    draw rectangle(16.2, 4.8) at: {56.5,yy} color: rgb(249,248,246);
                    draw line([{13.4,yy-2.35},{64.7,yy-2.35}]) color: rgb(184,195,207);
                    draw line([{13.4,yy+2.35},{64.7,yy+2.35}]) color: rgb(190,202,215);
                    draw rectangle(65.0, 1.0) at: {41.0,yy+3.25} color: rgb(131,150,171);
                    draw line([{8.5,yy+3.75},{13.0,yy+3.25}]) color: rgb(161,176,193);
                    draw (string(f+1) + "F") at: {3.0,yy+1.0} size: 7.2 color: rgb(32,58,87);
                    draw ("n=" + string(present)) at: {75.5,yy+1.2} size: 5.9 color: rgb(49,82,113);
                    // Density markers summarize real floor occupancy,
                    // not recorded visitor coordinates.
                    int dots <- min([30, int(float(present) / 8.0)]);
                    if (dots > 0) {
                        loop p from: 0 to: dots-1 {
                            float px <- 15.8 + float(p mod 15) * 3.1;
                            float py <- yy-1.2 + float(int(p/15)) * 2.3;
                            draw circle(0.55) at: {px,py} color: rgb(33,122,204);
                        }
                    }
                }
                // Vertical transfer symbols; their geometry is illustrative.
                loop b from: 0 to: 7 {
                    float lower_y <- 23.0 + (8-b) * 7.35;
                    float upper_y <- lower_y - 7.35;
                    draw line([{65.0,lower_y+0.5},{71.1,upper_y-0.5}])
                        color: rgb(49,123,196);
                    draw circle(0.9) at: {71.1,upper_y-0.5}
                        color: rgb(35,96,165);
                    int ub <- 0;
                    loop k from: 0 to: length(block_id)-1 {
                        loop m from: 0 to: 2 {
                            ub <- ub + truth_acc[((k*n_bnd+b)*2)*3+m];
                        }
                    }
                    draw ("U" + string(b+1) + ": " + string(ub))
                        at: {86.0,(lower_y+upper_y)/2.0+1.0} size: 5.7 color: rgb(27,78,126);
                }
                draw ("Day " + string(cur_day) + "  |  entered " + string(persons_entered)
                    + "  |  exited " + string(persons_exited)) at: {8.0,94.0}
                    size: 6.5 color: rgb(42,65,94);
                draw "SCHEMATIC | 1 dot approx. 8 people (max 30/floor) | no XY tracking"
                    at: {8.0,98.3} size: 5.8 color: rgb(104,115,129);
            }
        }
        monitor "Current tick" value: cycle;
        monitor "Groups in system" value: length(visitor);
        monitor "Persons entered today" value: persons_entered;
    }
}
