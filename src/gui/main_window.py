import warnings

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QLineEdit, QTextEdit

from src.gui.GUI import Ui_MainWindow
from src.utils.arrange_output import merge_fire
from src.utils.dynamic_program import coin_change
from src.utils.event_type import EventType
from src.utils.table_operation import set_pt_dict

warnings.filterwarnings("ignore", category=DeprecationWarning)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化pt达成方式字典
        self.pt_achieve_method: dict = {}

        # 初始化按钮状态
        self.ui.teamConfigButton.setChecked(True)

        # 功能切换按钮
        self.ui.teamConfigButton.clicked.connect(self.switch_to_page0)
        self.ui.autoPlanButton.clicked.connect(self.switch_to_page1)
        self.ui.settingButton.clicked.connect(self.switch_to_page2)

        # 添加配对按钮
        self.ui.addButton.clicked.connect(self.add_row_to_table)

        # 开始计算按钮
        self.ui.challengeStartCalc.clicked.connect(self.plan_challenge_live)
        self.ui.vsStartCalc.clicked.connect(self.plan_vs_live)
        self.ui.goalStartCalc.clicked.connect(self.plan_live_goals)
        self.ui.missionStartCalc.clicked.connect(self.plan_mission_live)
        self.ui.festivalStartCalc.clicked.connect(self.plan_team_live_festival)
        self.ui.medleyStartCalc.clicked.connect(self.plan_medley_live)

        # 设置表格列宽与行高
        self.ui.teamTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.ui.teamTable.horizontalHeader().setStretchLastSection(True)
        self.ui.teamTable.verticalHeader().setMinimumSectionSize(60)

    def switch_to_page0(self) -> None:
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.teamConfigButton.setChecked(True)
        self.ui.autoPlanButton.setChecked(False)
        self.ui.settingButton.setChecked(False)

    def switch_to_page1(self) -> None:
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.teamConfigButton.setChecked(False)
        self.ui.autoPlanButton.setChecked(True)
        self.ui.settingButton.setChecked(False)

    def switch_to_page2(self) -> None:
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.teamConfigButton.setChecked(False)
        self.ui.autoPlanButton.setChecked(False)
        self.ui.settingButton.setChecked(True)

    def add_row_to_table(self) -> None:
        band_name: str = self.ui.bandNameEdit.text()
        bonus: str = self.ui.bonusEdit.text()
        achivable_max: str = self.ui.achievableMaxEdit.text()
        support_team: str = self.ui.supportTeamEdit.text().strip() or ''

        inputs: list = [band_name, bonus, achivable_max, support_team]

        if self.validate_input_band(inputs):
            row_position: int = self.ui.teamTable.rowCount()
            self.ui.teamTable.insertRow(row_position)

            # 添加数据列
            for col, text in enumerate(inputs):
                item = QtWidgets.QTableWidgetItem(text)
                self.ui.teamTable.setItem(row_position, col, item)

            # 添加操作列
            btn_widget = QtWidgets.QWidget()
            btn_layout = QtWidgets.QHBoxLayout()

            delete_btn = QtWidgets.QPushButton("删除")

            delete_btn.clicked.connect(lambda _, r=row_position: self.delete_row(r))

            btn_layout.addWidget(delete_btn)
            btn_widget.setLayout(btn_layout)

            self.ui.teamTable.setCellWidget(row_position, 4, btn_widget)

            # 清空输入框
            self.clear_inputs()

    def validate_input_band(self, input_band: list[str]) -> bool:
        # 解包输入参数
        band_name: str = input_band[0]
        bonus: str = input_band[1]
        achivable_max: str = input_band[2]
        support_band: str = input_band[3]

        # 检测输入是否留空
        if band_name == '' or bonus == '' or achivable_max == '':
            QMessageBox.critical(self, '输入不完全', '除了副队综合力之外都是必填项！')
            return False

        # 检测输入是否是整数
        if not (bonus.isdigit()) or not (achivable_max.isdigit()) or not (support_band.isdigit()) and support_band != '':
            QMessageBox.critical(self, '非整数', '输入的内容不是整数！')
            return False

        # 检测输入是否是正数
        if int(bonus) < 0 or int(achivable_max) < 0 or (support_band != '' and int(support_band) < 0):
            QMessageBox.critical(self, '非正数', '输入的内容不是正数！')
            return False

        # 检测加成倍率的合理性
        if int(bonus) > 425:
            QMessageBox.critical(self, '加成倍率不合理', '输入的加成倍率超过了最大值！')
            return False

        return True

    def clear_inputs(self) -> None:
        self.ui.bandNameEdit.clear()
        self.ui.bonusEdit.clear()
        self.ui.achievableMaxEdit.clear()
        self.ui.supportTeamEdit.clear()

    def delete_row(self, row) -> None:
        self.ui.teamTable.removeRow(row)

    def update_pt_dict(self, event_type: EventType) -> bool:
        try:
            self.pt_achieve_method = set_pt_dict(event_type, self.ui.teamTable)
            return True
        except Exception as e:
            QMessageBox.critical(self, "错误", f"获取 pt 数据失败：{e}")
            return False

    def challenge_live_dict(self) -> None:
        self.update_pt_dict(EventType.CHALLENGE_LIVE)

    def vs_live_dict(self) -> None:
        self.update_pt_dict(EventType.VS_LIVE)

    def live_goals_dict(self) -> None:
        self.update_pt_dict(EventType.LIVE_GOALS)

    def mission_live_dict(self) -> None:
        self.update_pt_dict(EventType.MISSION_LIVE)

    def team_live_festival_dict(self) -> None:
        self.update_pt_dict(EventType.TEAM_LIVE_FESTIVAL)

    def medley_live_dict(self) -> None:
        self.update_pt_dict(EventType.MEDLEY_LIVE)

    def plan(self, current_pt: int, target_pt: int) -> list[dict]:
        diff: int = target_pt - current_pt
        if diff < 0:
            QMessageBox.information(self, "提示", "当前活动pt已超过目标pt")
            return []
        if diff == 0:
            QMessageBox.information(self, "提示", "无需额外游玩即可达到目标pt")
            return []

        coins: list[int] = list(self.pt_achieve_method.keys())
        plan_coins: list[int] = coin_change(coins, diff)

        if not plan_coins:
            return []

        combination: list[dict] = []
        for coin in plan_coins:
            config: dict = self.pt_achieve_method[coin]
            combination.append({
                "pt": coin,
                "band_name": config["band_name"],
                "score_range": (config["lower_limit"], config["upper_limit"])
            })
        return combination

    def show_plan(self, current_edit: QLineEdit, target_edit: QLineEdit, result_widget: QTextEdit) -> None:
        try:
            current_pt = int(current_edit.text().strip())
            target_pt = int(target_edit.text().strip())
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的整数 pt 数值。")
            return

        combination = self.plan(current_pt, target_pt)
        if not combination:
            result_widget.setText("无法生成有效方案，请尝试添加更多队伍，或随便打一把以便重新规划。")
            return

        # 每局默认0火
        rounds = [{**item, "fire": 0} for item in combination]
        final_rounds = merge_fire(rounds)

        result_str = "最优方案（共游玩 {} 局）：\n".format(len(final_rounds))
        for idx, item in enumerate(final_rounds, start=1):
            result_str += "第 {} 局： {} pt, 队伍： {}, 分数范围： {} ~ {}，使用 {} 火\n".format(
                idx, item["pt"], item["band_name"],
                item["score_range"][0], item["score_range"][1],
                item["fire"]
            )
        result_widget.setText(result_str)

    def plan_challenge_live(self) -> None:
        self.challenge_live_dict()
        self.show_plan(self.ui.challengeCurrentEdit, self.ui.challengeTargetEdit, self.ui.challengeResult)

    def plan_vs_live(self) -> None:
        self.vs_live_dict()
        self.show_plan(self.ui.vsCurrentEdit, self.ui.vsTargetEdit, self.ui.vsResult)

    def plan_live_goals(self) -> None:
        self.live_goals_dict()
        self.show_plan(self.ui.goalCurrentEdit, self.ui.goalTargetEdit, self.ui.goalResult)

    def plan_mission_live(self) -> None:
        self.mission_live_dict()
        self.show_plan(self.ui.missionCurrentEdit, self.ui.missionTargetEdit, self.ui.missionResult)

    def plan_team_live_festival(self) -> None:
        self.team_live_festival_dict()
        self.show_plan(self.ui.festivalCurrentEdit, self.ui.festivalTargetEdit, self.ui.festivalResult)

    def plan_medley_live(self) -> None:
        self.medley_live_dict()
        self.show_plan(self.ui.medleyCurrentEdit, self.ui.medleyTargetEdit, self.ui.medleyResult)
