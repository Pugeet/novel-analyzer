"""
多模型LLM客户端 — 支持 Claude + DeepSeek，统一接口
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
import os


class NovelLLM:
    """统一LLM调用接口，支持 Claude / DeepSeek"""

    def __init__(self, model: str = "claude"):
        self.model_choice = model

    def _get_claude(self):
        return ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.7,
            max_tokens=4096,
        )

    def _get_deepseek(self):
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
        return OpenAI(
            api_key=key,
            base_url="https://api.deepseek.com",
        )

    def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """同步调用"""
        if self.model_choice == "claude":
            llm = self._get_claude()
            prompt = ChatPromptTemplate.from_messages([
                ("system", "{system_prompt}"),
                ("human", "{input}"),
            ])
            chain = prompt | llm | StrOutputParser()
            return chain.invoke({"system_prompt": system_prompt, "input": user_prompt})

        elif self.model_choice == "deepseek":
            client = self._get_deepseek()
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
            )
            return resp.choices[0].message.content

        else:
            raise ValueError(f"Unknown model: {self.model_choice}")

    def stream(self, system_prompt: str, user_prompt: str):
        """流式调用（生成器）"""
        if self.model_choice == "claude":
            llm = self._get_claude()
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])
            chain = prompt | llm | StrOutputParser()
            yield from chain.stream({"input": user_prompt})

        elif self.model_choice == "deepseek":
            client = self._get_deepseek()
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=4096,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
