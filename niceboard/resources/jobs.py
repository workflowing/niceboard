# src/niceboard/resources/jobs.py
from typing import Dict, Any, List, Optional
from ..resource import Resource
import json


class Jobs(Resource):
    def list(
        self,
        page: int = 1,
        limit: int = 30,
        jobtype: Optional[str] = None,
        company: Optional[str] = None,
        category: Optional[str] = None,
        secondary_category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        location: Optional[str] = None,
        remote_ok: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params = {
            "page": page,
            "limit": limit,
            "jobtype": jobtype,
            "company": company,
            "category": category,
            "secondary_category": secondary_category,
            "location": location,
            "remote_ok": remote_ok,
            "is_featured": is_featured,
            "keyword": keyword,
        }

        if tags:
            params["tags"] = json.dumps(tags)

        params = {k: v for k, v in params.items() if v is not None}

        response = self._make_request("GET", "jobs", params=params)
        data = response.json()
        jobs = data.get("results", {}).get("jobs", [])
        return [self.add_job_fields(job) for job in jobs]

    def create(
        self,
        company_id: int,
        jobtype_id: int,
        title: str,
        apply_by_form: bool,
        description_html: str,
        **kwargs,
    ) -> Dict[str, Any]:
        payload = {
            "company_id": company_id,
            "jobtype_id": jobtype_id,
            "title": title,
            "apply_by_form": apply_by_form,
            "description_html": description_html,
            **kwargs,
        }
        response = self._make_request("POST", "jobs", data=payload)
        return response.json()

    def get(self, job_id: int) -> Dict[str, Any]:
        response = self._make_request("GET", f"jobs/{job_id}")
        result = response.json()
        job = result.get("results", {}).get("job", {})
        if job:
            job = self.add_job_fields(job)
        return job

    def update(self, job_id: int, **kwargs) -> Dict[str, Any]:
        response = self._make_request("PATCH", f"jobs/{job_id}", data=kwargs)
        return response.json()

    def delete(self, job_id: int) -> Dict[str, Any]:
        response = self._make_request("DELETE", f"jobs/{job_id}")
        return response.json()

    def add_job_fields(self, job: Dict[str, Any]) -> Dict[str, Any]:
        job["published_url"] = f"{self.base_job_url}/{job['id']}-{job['slug']}"
        return job
