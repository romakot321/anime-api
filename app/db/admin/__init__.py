from fastapi import FastAPI
from sqladmin import Admin
from .views import TaskView, PromptView, TaskImageView, TaskItemView
from .auth import authentication_backend
from sqlalchemy_service.base_db.base import engine


def attach_admin_panel(application: FastAPI):
    admin = Admin(application, engine, authentication_backend=authentication_backend)

    admin.add_view(TaskView)
    admin.add_view(PromptView)
    admin.add_view(TaskImageView)
    admin.add_view(TaskItemView)

