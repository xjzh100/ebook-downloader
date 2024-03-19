import flet as ft
from common import open_snack_bar, BookHelper


class Book(ft.UserControl):
    def __init__(self, page, term, helper: BookHelper):
        super().__init__()
        self.page = page
        self.term = term
        self.helper = helper
        self.term_id = term.get('tag_id')
        self.title = term.get('tag_name')
        self.text = ft.Text(f'{self.title}', size=20)
        self.buttonStyle = ft.ButtonStyle(
            color={
                ft.MaterialState.FOCUSED: ft.colors.WHITE,
                ft.MaterialState.SELECTED: ft.colors.WHITE,
                ft.MaterialState.DEFAULT: ft.colors.BLACK,
            },
            bgcolor={
                ft.MaterialState.FOCUSED: ft.colors.BLUE,
                ft.MaterialState.SELECTED: ft.colors.BLUE,
            },
        )

        self.listView = ft.ListView(expand=True, spacing=10)

        self.subjectOptions = []
        self.versionOptions = []
        self.gradeOptions = []

        self.subjectDropdown = ft.Dropdown(
            width=180,
            label="学科",
            hint_text="请选择学科",
            options=self.subjectOptions,
            on_change=self.dropdown_changed,
        )
        self.versionDropdown = ft.Dropdown(
            width=400,
            label="版本",
            hint_text="请选择版本",
            options=self.versionOptions,
            on_change=self.dropdown_changed,
        )
        self.gradeDropdown = ft.Dropdown(
            width=180,
            label="年级",
            hint_text="请选择年级",
            options=self.gradeOptions,
            on_change=self.dropdown_changed,
        )

        self.controls = [
            self.text,
            ft.Row(
                [
                    self.subjectDropdown,
                    self.versionDropdown,
                    self.gradeDropdown,
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY
            ),
            ft.Divider(),
            self.listView,
        ]

    def init(self):
        # 初始化学科下拉框
        self.subjectOptions.clear()
        for k, v in self.helper.get_subject(self.term_id).items():
            self.subjectOptions.append(
                ft.dropdown.Option(text=v["tag_name"], key=k)
            )
        self.subjectDropdown.value = self.subjectOptions[0].key
        # 初始化版本下拉框
        self.render_version_options(self.subjectDropdown.value)
        # 初始化年级下拉框
        self.render_grade_options(self.versionDropdown.value)
        # 渲染布局
        self.render_view()

    def on_click(self, e):
        # 全局 ProgressBar
        # self.page.controls[1].visible = True
        # self.page.update()
        progress_bar = next(filter(lambda control: control.data == e.control.data['id'], self.listView.controls)) \
            .controls[0].controls[1].content.controls[3]
        self.helper.download(progress_bar, e)

    def dropdown_changed(self, e):
        value = e.control.value
        if e.control.label == '学科':
            self.render_version_options(value)
            self.render_grade_options(self.versionDropdown.value)
        if e.control.label == '版本':
            self.render_grade_options(value)
        # 重新渲染数据
        self.render_view()

    def render_version_options(self, sub_id):
        self.versionOptions.clear()
        for k, v in self.helper.get_version(self.term_id, sub_id).items():
            self.versionOptions.append(
                ft.dropdown.Option(text=v["tag_name"], key=k)
            )
        self.versionDropdown.value = self.versionOptions[0].key

    def render_grade_options(self, version_id):
        self.gradeOptions.clear()
        grades = self.helper.get_grade(self.term_id, self.subjectDropdown.value, version_id)
        if grades:
            self.gradeDropdown.visible = True
            for k, v in grades.items():
                self.gradeOptions.append(
                    ft.dropdown.Option(text=v["tag_name"], key=k)
                )
            self.gradeDropdown.value = self.gradeOptions[0].key
        else:
            self.gradeDropdown.visible = False

    def render_view(self):
        if self.gradeDropdown.visible:
            search_str = '/'.join(
                [self.term_id, self.subjectDropdown.value, self.versionDropdown.value, self.gradeDropdown.value])
        else:
            search_str = '/'.join([self.term_id, self.subjectDropdown.value, self.versionDropdown.value])
        books = self.helper.get_books(search_str)
        containers = []
        for item in books:
            container = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Image(
                                src=f"{item['thumbnails']}",
                                width=300,
                                height=240,
                                border_radius=ft.border_radius.all(10),
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text(f"{item['title']}", size=18, weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            content=ft.Row(
                                                [
                                                    ft.Icon(ft.icons.BUSINESS, size=14, color='#cccccc'),
                                                    ft.Text("智慧中小学", size=14, color='#cccccc'),
                                                    ft.Icon(ft.icons.THUMB_UP, size=14, color='#cccccc'),
                                                    ft.Text(f"{item['like_count']}", size=14, color='#cccccc'),
                                                    ft.Icon(ft.icons.REMOVE_RED_EYE_OUTLINED, size=14, color='#cccccc'),
                                                    ft.Text(f"{item['total_uv']}", size=14, color='#cccccc')
                                                ]
                                            )
                                        ),
                                        ft.Row(
                                            [
                                                ft.ElevatedButton(
                                                    icon=ft.icons.PREVIEW,
                                                    text='预览',
                                                    data=item,
                                                    style=self.buttonStyle,
                                                    icon_color=ft.colors.BLUE,
                                                    # on_click=self.on_click,
                                                    on_click=lambda e: open_snack_bar(self.page, "功能开发中，敬请期待！"),
                                                    tooltip='预览'
                                                ),
                                                ft.ElevatedButton(
                                                    icon=ft.icons.CLOUD_DOWNLOAD,
                                                    text='下载',
                                                    data=item,
                                                    style=self.buttonStyle,
                                                    icon_color=ft.colors.BLUE,
                                                    on_click=self.on_click,
                                                    tooltip='下载'
                                                ),
                                            ]
                                        ),
                                        ft.ProgressBar(width=400, color="blue", bgcolor="#eeeeee", visible=False)
                                    ],
                                    height=240,
                                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                )
                            ),
                        ],
                        height=240
                    ),
                    ft.Divider(),
                ],
                data=item['id']
            )
            containers.append(container)

        self.listView.controls = containers
        self.page.update()
