"""Download functionality for the arXiv MCP server."""
import arxiv
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import mcp.types as types
import pymupdf4llm
from pdf2zh.high_level import translate
from pdf2zh.config import ConfigManager
from pdf2zh.doclayout import OnnxModel
from paper_report_mcp.config import Settings
from paper_report_mcp.logger import logger
from paper_report_mcp.utils import get_exception_error, root_dir
import requests
import time

settings = Settings()
proxies = {'http': settings.PROXY, 'https': settings.PROXY}


download_tool = types.Tool(
    name="download_paper",
    description="Download a paper and create a resource for it",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv ID of the paper to download",
            }
        },
        "required": ["paper_id"],
    },
)


def get_paper_path(paper_id: str, suffix: str = ".md") -> Path:
    """Get the absolute file path for a paper with given suffix."""
    storage_path = Path(settings.STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path / f"{paper_id}{suffix}"


def convert_pdf_to_markdown(paper_id: str, pdf_path: Path) -> None:
    """Convert PDF to Markdown in a separate thread."""
    try:
        logger.info(f"Starting conversion for {paper_id}")
        markdown = pymupdf4llm.to_markdown(pdf_path, show_progress=False)
        md_path = get_paper_path(paper_id, ".md")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Clean up PDF after successful conversion
        logger.info(f"Conversion completed for {paper_id}")

    except Exception as e:
        error_msg = get_exception_error()
        logger.error(f"Conversion failed for {paper_id}:\n{error_msg}")
        raise e


async def handle_download(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle paper download and conversion requests."""
    paper_id = arguments.get("paper_id", "")
    try:
        # Check if paper is already converted
        if get_paper_path(paper_id, ".md").exists():
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "success",
                            "message": "Paper already available",
                            "resource_uri": f"file://{get_paper_path(paper_id, '.md')}",
                        }
                    ),
                )
            ]

        # Start new download and conversion
        pdf_path = get_paper_path(paper_id, ".pdf")
        client = arxiv.Client()
        client._session.proxies = proxies

        # Initialize status
        start_at = datetime.now()

        # Download PDF
        paper = next(client.results(arxiv.Search(id_list=[paper_id])))
        logger.debug(f"paper downloading: {paper}")
        pdf_url = arxiv.Result._substitute_domain(paper.pdf_url, "export.arxiv.org")
        download_pdf(pdf_url, pdf_path)

        # Translate PDF
        translate_pdf(paper_id, pdf_path)

        zh_pdf = get_paper_path(paper_id, "-mono.pdf")
        # Convert PDF
        convert_pdf_to_markdown(paper_id, zh_pdf)
        end_at = datetime.now()

        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success",
                        "message": "Paper downloaded, conversion success",
                        "start": start_at.isoformat(),
                        "end": end_at.isoformat()
                    }
                ),
            )
        ]

    except StopIteration:
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Paper {paper_id} not found on arXiv",
                    }
                ),
            )
        ]
    except Exception as e:
        error_msg = get_exception_error()
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "message": f"{error_msg}"}),
            )
        ]


def download_pdf(url, local_file):
    logger.info(f"begin to download pdf from url={url} to {local_file}")

    try:
        # 获取文件大小
        with requests.get(url, proxies=proxies, stream=True, timeout=settings.REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            logger.debug(f"pdf file total size: {total_size}")

            # 开始下载
            with open(local_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # 过滤保持连接的空白块
                        f.write(chunk)
        time.sleep(1)
        logger.info("pdf file download success!")
    except requests.exceptions.RequestException as e:
        error_msg = get_exception_error()
        logger.error(f"download pdf error: {error_msg}")
        raise e
    except Exception as e:
        error_msg = get_exception_error()
        logger.error(f"download pdf error: {error_msg}")
        raise e


def translate_pdf(paper_id, pdf_path):
    files = [str(pdf_path.absolute())]
    # config.json
    config_file = root_dir + "/config/config.json"
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            conf_data = json.load(f)
    except FileNotFoundError:
        conf_data = {}  # 如果文件不存在，则初始化为空字典

    conf_data["NOTO_FONT_PATH"] = root_dir + "/fonts/SourceHanSerifCN-Regular.ttf"
    with open(config_file, 'w', encoding='utf-8') as f:
        # 使用 indent=4 使JSON文件格式化，更易读
        json.dump(conf_data, f, indent=4, ensure_ascii=False)
    logger.info(f"modify {config_file} success.")
    ConfigManager.custome_config(config_file)

    # omni
    model = OnnxModel(root_dir + "/models/doclayout_yolo_docstructbench_imgsz1024.onnx")
    # envs
    envs = {"https_proxy": settings.PROXY, "http_proxy": settings.PROXY}

    translate(
        files=files,
        output=root_dir + "/downloads",
        lang_in="en",
        lang_out="zh",
        service="google",
        thread=4,
        model=model,
        envs=envs
    )

    # check if -mono.pdf exist
    zh_pdf = get_paper_path(paper_id, "-mono.pdf")
    if Path.is_file(zh_pdf):
        return True
    else:
        raise Exception(f"translate {paper_id}.pdf to Chinese error.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(handle_download({"paper_id": "2509.08721"}))
