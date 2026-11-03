"""슬라이드 HTML을 Modal에서 Chromium + Pretendard로 렌더링한다 (Claude 토큰이 아니라 Modal 크레딧을 쓴다).

    modal run modal_render.py --src <slide.html> --out <출력 경로(확장자 없이)> [--scale 2]

한 파일이면 한 컨테이너, 여러 파일을 쉼표로 주면 컨테이너가 파일 수만큼 병렬로 뜬다.
각 슬라이드는 1920x1080(16:9) 고정, device_scale_factor=2 로 3840x2160 PNG와 벡터 PDF를 만든다.
"""
import os

import modal

FONT_DIR = r"C:\Users\admin\AppData\Local\Microsoft\Windows\Fonts"
WEIGHTS = ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold"]

app = modal.App("thesis-slides-render")

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("fontconfig")
    .pip_install("playwright==1.49.0")
    .run_commands("playwright install --with-deps chromium")
)
for w in WEIGHTS:
    image = image.add_local_file(os.path.join(FONT_DIR, f"Pretendard-{w}.ttf"),
                                 f"/usr/share/fonts/truetype/pretendard/Pretendard-{w}.ttf", copy=True)
image = image.run_commands("fc-cache -f && fc-list | grep -c Pretendard")


@app.function(image=image, cpu=8, memory=8192, timeout=900)
def render(html: str, scale: float = 2.0, w: int = 1920, h: int = 1080) -> dict:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        page.set_content(html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        # 실제로 Pretendard 글리프가 쓰였는지 확인(대체 글꼴이면 레이아웃이 달라진다)
        used = page.evaluate("""async () => {
            const c = await (async () => { try { return document.fonts.check('700 20px Pretendard'); } catch (e) { return null; } })();
            return c;
        }""")
        png = page.screenshot(type="png", clip={"x": 0, "y": 0, "width": w, "height": h})
        pdf = page.pdf(width=f"{w}px", height=f"{h}px", print_background=True, page_ranges="1")
        browser.close()
    return {"png": png, "pdf": pdf, "pretendard_check": used}


@app.local_entrypoint()
def main(src: str, out: str, scale: float = 2.0):
    srcs = [s for s in src.split(",") if s]
    outs = [o for o in out.split(",") if o]
    assert len(srcs) == len(outs), "src와 out 개수가 같아야 합니다"
    htmls = [open(s, encoding="utf-8").read() for s in srcs]
    for o, res in zip(outs, render.map(htmls, kwargs={"scale": scale})):
        with open(o + ".png", "wb") as fh:
            fh.write(res["png"])
        with open(o + ".pdf", "wb") as fh:
            fh.write(res["pdf"])
        print("saved:", os.path.abspath(o + ".png"))
        print("saved:", os.path.abspath(o + ".pdf"))
        print("pretendard check:", res["pretendard_check"])
