from app.db.tables import Task, Prompt, TaskItem, TaskImage
from sqladmin import ModelView


class TaskView(ModelView, model=Task):
    column_list = "__all__"
    column_searchable_list = [Task.id, Task.user_id, Task.app_bundle]
    column_default_sort = [(Task.created_at, True)]


class TaskImageView(ModelView, model=TaskImage):
    column_list = "__all__"
    column_searchable_list = [TaskImage.id]
    column_default_sort = [(TaskImage.created_at, True)]


class TaskItemView(ModelView, model=TaskItem):
    column_list = "__all__"
    column_searchable_list = [TaskItem.id]


class PromptView(ModelView, model=Prompt):
    column_list = "__all__"
    column_searchable_list = [Prompt.id, Prompt.title]
    column_default_sort = [(Prompt.created_at, True)]

