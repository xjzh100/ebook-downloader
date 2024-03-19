import flet as ft
from book import Book
from common import BookHelper, open_snack_bar


class App:

    def __init__(self, page, helper: BookHelper):
        self.page = page
        self.view_index_map = {}
        self.navigationRailDestinations = []
        # 获取学段数据
        terms = helper.get_term()
        # 初始化左侧导航栏条目
        for index, item in enumerate(terms):
            self.view_index_map[index] = Book(page, terms[item], helper)
            text = terms[item]['tag_name']
            self.navigationRailDestinations.append(
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.SCHOOL_OUTLINED, size=28, tooltip=f'{text}'),
                    selected_icon_content=ft.Icon(ft.icons.SCHOOL, size=28, color=ft.colors.BLUE),
                    label_content=ft.Text(f'{text}', size=16),
                )
            ),

        # 免责声明
        self.navigationRailDestinations.append(
            ft.NavigationRailDestination(
                icon_content=ft.Icon(ft.icons.HELP_OUTLINE, size=28, tooltip='免责声明'),
                selected_icon_content=ft.Icon(ft.icons.HELP, size=28, color=ft.colors.BLUE),
                label_content=ft.Text('免责声明', size=16),
            )
        ),

        # 初始化左侧导航栏
        self.Navigation = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=400,
            group_alignment=-0.9,
            destinations=self.navigationRailDestinations,
            on_change=self.refresh_body,
        )
        self.body = ft.Column(
            controls=self.view_index_map.get(self.Navigation.selected_index).controls,
            expand=True,
        )
        # 设置默认页面内容
        self.view_index_map.get(self.Navigation.selected_index).init()
        self.page.snack_bar = ft.SnackBar(content=ft.Text(''))
        self.page.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("免责声明"),
            content=ft.Text(
                "本软件开源免费，严禁盗卖！任何个人或组织不得将本软件用于商业用途。\n"
                "本软件中所涉及的技术仅供学习交流，任何个人或组织不得对国家中小学智慧教育平台进行大规模数据爬取。\n"
                "对于违反相关法律，造成危害的滥用行为，本人不承担任何法律责任。\n"
                "使用本软件即表示您同意本免责声明中的所有条款。"),
            actions=[
                ft.TextButton("确定", key='agree', on_click=self.close_dialog),
                # ft.TextButton("取消", key='disagree', on_click=self.close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        # 顶部导航
        self.page.appbar = ft.AppBar(
            # leading=ft.Image(src='https://basic.smartedu.cn/img/logo-icon.afa526cf.png', tooltip='国家中小学教材'),
            # leading_width=40,
            # title=ft.Text('国家中小学教材'),
            title=ft.Image(src='https://basic.smartedu.cn/img/logo-new-default.59a73b97.png', width=260, height=35),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(ft.icons.WB_SUNNY_OUTLINED, on_click=self.change_theme, tooltip='切换主题'),
                ft.IconButton(ft.icons.HELP_OUTLINE, url='https://github.com/v5tech/ebook-downloader', tooltip='开源地址'),
            ],
        )
        # 全局 ProgressBar
        self.progressBar = ft.ProgressBar(color="blue", bgcolor="#eeeeee", visible=False)
        self.page.add(
            ft.Row(
                [
                    self.Navigation,
                    ft.VerticalDivider(width=1),
                    self.body,
                ],
                expand=True,
            ),
            self.progressBar
        )
        open_snack_bar(page, f"共找到 {len(helper.books)} 本电子教材！")

    def refresh_body(self, e):
        """
        刷新内容区域
        """
        selected_index = e.control.selected_index
        view = self.view_index_map.get(selected_index)
        if view:
            self.body.controls = view.controls
            view.init()
            # open_snack_bar(self.page, f'{e.control.destinations[selected_index].label_content.value}')
        else:
            self.page.dialog.open = True
        self.page.update()

    def change_theme(self, e):
        """
        切换主题
        """
        if self.page.theme_mode == ft.ThemeMode.LIGHT.value:
            self.page.theme_mode = ft.ThemeMode.DARK.value
            open_snack_bar(self.page, '深色主题')
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT.value
            open_snack_bar(self.page, '浅色主题')
        self.page.client_storage.set('theme', self.page.theme_mode)
        self.page.update()

    def show_warning(self):
        """
        显示免责声明
        """
        is_show = self.page.client_storage.get('is_show')
        if is_show is None:
            is_show = True
            self.page.client_storage.set('is_show', is_show)
        if is_show:
            self.page.dialog.open = True
            self.page.client_storage.set('is_show', False)
            self.page.update()

    def close_dialog(self, e):
        """
        关闭AlertDialog
        """
        self.page.dialog.open = False
        self.page.update()


def main(page: ft.Page):
    theme = page.client_storage.get('theme')
    if theme is None:
        theme = ft.ThemeMode.LIGHT.value
        page.client_storage.set('theme', theme)

    page.title = '国家中小学教材下载'
    page.auto_scroll = True
    page.theme_mode = theme
    page.window_width = 1024
    page.window_height = 768
    page.window_maximizable = False
    page.window_resizable = False

    # 实例化BookHelper
    helper = BookHelper()

    app = App(page, helper)
    app.show_warning()


if __name__ == '__main__':
    ft.app(target=main, assets_dir='assets')
