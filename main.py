import os
import pymupdf4llm 
from pathlib import Path
from dotenv import load_dotenv

from src.llm.llm import LLM
from src.notion.crud import NotionRepository

load_dotenv()
WORK_DIR = Path(os.environ.get("WORK_DIR"))
PROMPT_DIR = WORK_DIR / "prompts"

def test():
    llm_client: LLM = LLM(base="openai", model="gpt-4o-mini")
    notion: NotionRepository = NotionRepository()

    paper_path: Path = Path("/PaperSurvey/docs/prototype/Augmenting Automated Game Testing with Deep Reinforcement Learning.pdf")
    title = paper_path.stem[0: len(str(paper_path))-4]
    paper_md: str = pymupdf4llm.to_markdown(paper_path)
     
    prompt_path: Path = PROMPT_DIR / "v1.txt"
    prompt: str = open(prompt_path).read()
    prompt = prompt.replace("<<INPUT>>", paper_md)

    llm_client.set_prompt(text=prompt)
    md_content, input_tokens, output_tokens = llm_client.get_response()

    notion.create_markdown_page(title, md_content)

    print(input_tokens, output_tokens)
    print(150 * 0.15 * input_tokens / 1000000 + 150 * 0.6 *  output_tokens / 1000000)

    return

if __name__ == "__main__":
    test()



    

