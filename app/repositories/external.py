from typing import BinaryIO
from aiohttp import ClientSession
import os
from uuid import uuid4

from loguru import logger

from app.schemas.external import ExternalImageGeneration, ExternalVideoGeneration


class ExternalRepository:
    image_api_url = os.getenv("IMAGE_API_URL")
    image_api_token = os.getenv("IMAGE_API_TOKEN")
    video_api_url = os.getenv("VIDEO_API_URL").rstrip("/")
    video_api_token = os.getenv("VIDEO_API_TOKEN")

    user_id: str = str(uuid4())
    app_bundle: str = "animeapi"

    async def start_image_generate(self, prompt: str) -> str:
        """Return task_id"""
        async with ClientSession(base_url=self.image_api_url, headers={"ACCESS-TOKEN": self.image_api_token}) as session:
            resp = await session.post(
                "/image",
                json={
                    "prompt": prompt,
                    "user_id": self.user_id,
                    "app_bundle": self.app_bundle,
                    "image_size": "portrait_4_3"
                }
            )
            assert resp.status == 201, await resp.text()
            return (await resp.json())["id"]

    async def get_image_generation(self, task_id: str) -> ExternalImageGeneration:
        async with ClientSession(base_url=self.image_api_url, headers={"ACCESS-TOKEN": self.image_api_token}) as session:
            resp = await session.get("/image/" + task_id)
            assert resp.status == 200, await resp.text()
            schema = ExternalImageGeneration.model_validate(await resp.json())
        logger.debug(f"Image API response: {schema.model_dump()}")
        return schema

    async def upload_image_for_video(self, image_buffer: BinaryIO) -> str:
        """Return image_id"""
        async with ClientSession(base_url=self.video_api_url, headers={"ACCESS-TOKEN": self.video_api_token}) as session:
            resp = await session.post(
                "/image",
                data={'file': image_buffer}
            )
            assert resp.status == 201, await resp.text()
            logger.debug("Image uploaded")
            return (await resp.json())["id"]

    async def start_video_generate(self, prompt: str, image_id: str) -> str:
        """Return task_id"""
        async with ClientSession(base_url=self.video_api_url, headers={"ACCESS-TOKEN": self.video_api_token}) as session:
            resp = await session.post(
                "/video",
                json={
                    "prompt": prompt,
                    "image_url": self.video_api_url + "/image/" + image_id,
                    "user_id": self.user_id,
                    "app_bundle": self.app_bundle,
                }
            )
            assert resp.status == 201, await resp.text()
            logger.debug("Video generation started")
            return (await resp.json())["id"]

    async def get_video_generation(self, task_id: str) -> ExternalVideoGeneration:
        async with ClientSession(base_url=self.video_api_url, headers={"ACCESS-TOKEN": self.video_api_token}) as session:
            resp = await session.get("/video/" + task_id)
            assert resp.status == 200, await resp.text()
            schema = ExternalVideoGeneration.model_validate(await resp.json())
        logger.debug("Video response: " + str(schema.model_dump()))
        return schema

    @classmethod
    def make_video_url(cls, task_id: str) -> str:
        return f'{cls.video_api_url}/video/file/{task_id}'

