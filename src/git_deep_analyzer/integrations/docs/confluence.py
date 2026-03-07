"""Confluence docs system integration."""

import requests
from typing import List, Optional
from datetime import datetime
from .base import DocsSystemBase
from .models import Document


class ConfluenceDocs(DocsSystemBase):
    """Confluence文档系统集成"""

    def __init__(self, config: dict, ai_client=None):
        super().__init__(config, ai_client)
        self.base_url = config["url"]
        self.token = config.get("token", "")
        self.space_key = config.get("space_key")
        self.session = None

    def connect(self) -> bool:
        """连接到Confluence"""
        import os

        self.session = requests.Session()

        # 支持多种认证方式
        if self.token:
            # Personal Access Token
            self.session.auth = (config.get("email", ""), self.token)
        elif os.environ.get("CONFLUENCE_TOKEN"):
            self.session.auth = ("", os.environ["CONFLUENCE_TOKEN"])
        elif config.get("username") and config.get("password"):
            # Basic Auth
            self.session.auth = (config["username"], config["password"])

        self.session.headers.update({
            "Accept": "application/json"
        })

        # 测试连接
        try:
            response = self.session.get(f"{self.base_url}/rest/api/user/current")
            return response.status_code == 200
        except Exception:
            return False

    def fetch_documents(
        self,
        since=None,
        until=None,
        labels=None,
        space_key=None
    ) -> List[Document]:
        """获取文档列表"""
        pk = space_key or self.space_key
        if not pk:
            raise ValueError("Space key is required")

        # 使用CQL查询
        cql_parts = []
        cql_parts.append(f'space.key = "{pk}"')

        if since:
            cql_parts.append(f'created >= "{since.strftime("%Y-%m-%d")}"')

        if until:
            cql_parts.append(f'created <= "{until.strftime("%Y-%m-%d")}"')

        if labels:
            label_query = " or ".join([f'label = "{l}"' for l in labels])
            cql_parts.append(f"({label_query})")

        cql = " and ".join(cql_parts)

        url = f"{self.base_url}/rest/api/content/search"
        params = {
            "cql": cql,
            "expand": "version,space,labels",
            "limit": 100
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Confluence API error: {response.text}")

        data = response.json()

        # 解析文档
        documents = []
        for page_data in data.get("results", []):
            documents.append(self._parse_document(page_data))

        return documents

    def fetch_document_detail(self, document_id: str) -> Document:
        """获取文档详情"""
        url = f"{self.base_url}/rest/api/content/{document_id}"
        params = {
            "expand": "version,space,ancestors"
        }

        response = self.session.get(url, params=params, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Confluence API error: {response.text}")

        data = response.json()
        return self._parse_document(data)

    def _parse_document(self, page_data: dict) -> Document:
        """解析文档数据"""
        return Document(
            id=page_data["id"],
            title=page_data["title"],
            content=self._extract_content(page_data),
            type=self._infer_type(page_data),
            created_at=datetime.fromisoformat(page_data["version"]["createdWhen"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(page_data["version"]["when"].replace("Z", "+00:00")),
            author=page_data["version"]["by"]["displayName"],
            author_email=page_data["version"]["by"].get("emailAddress", ""),
            space_key=page_data["space"]["key"],
            url=f"{self.base_url}{page_data['_links']['webui']}"
        )

    def _extract_content(self, page_data: dict) -> dict:
        """提取文档内容（简化版，实际需要额外API调用）"""
        # 简化实现：假设内容在page_data中
        # 实际需要调用 content API
        return page_data.get("body", {}).get("storage", {}).get("value", "")

    def _infer_type(self, page_data: dict) -> str:
        """推断文档类型"""
        title = page_data.get("title", "").lower()
        labels = [l.get("name", "").lower() for l in page_data.get("labels", {}).get("results", [])]

        if any(word in title or word in str(labels) for word in ["需求", "requirement", "prd", "user story"]):
            return DocumentType.REQUIREMENT
        elif any(word in title or word in str(labels) for word in ["设计", "design", "架构", "architecture"]):
            return DocumentType.DESIGN
        elif any(word in title or word in str(labels) for word in ["规格", "spec", "规格说明"]):
            return DocumentType.SPEC
        elif "api" in title or "接口" in title:
            return DocumentType.API
        else:
            return DocumentType.OTHER
