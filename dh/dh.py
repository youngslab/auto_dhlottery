
from enum import Enum
from integ_auto import *
from .lotto645 import *


class Lottery(Enum):
    lotto645 = "로또6/45"
    game720 = "연금복권720"


def dh_login(auto: Automatic, id, pw):
    auto.go('https://dhlottery.co.kr/common.do?method=main')

    login_btn = auto.get_element(By.XPATH, '//a[text()="로그인"]')
    if not login_btn:
        print("Failed to find login button.")
        return False
    auto.click(login_btn)

    pw_input = auto.get_element(By.XPATH, '//input[@title="비밀번호"]')
    if not pw_input:
        print("Failed to find pw input.")
        return False
    auto.type(pw_input, pw)

    id_input = auto.get_element(By.XPATH, '//input[@title="아이디"]')
    if not id_input:
        print("Failed to find id input.")
        return False
    auto.type(id_input, id)

    login_btn = auto.get_element(
        By.XPATH, '//div[@class="form"]/a[text()="로그인"]')
    if not login_btn:
        print("Failed to find login button.")
        return False
    auto.click(login_btn)

    return True


def dh_get_maximum_purchase(lottery: Lottery):
    if lottery == Lottery.lotto645:
        return 5
    # TODO: implement game720
    else:
        return 0


def dh_get_num_of_purchase_left(auto: Automatic, lottery:  Lottery):

    # 구매내역
    auto.go("https://www.dhlottery.co.kr/myPage.do?method=lottoBuyListView")

    # 1주일
    oneweek_btn = auto.get_element(
        By.XPATH, '//*[@id="frm"]/table/tbody/tr[3]/td/span[2]/a[2]')
    if not oneweek_btn:
        print("Error: Failed to find 1주일 button")
        return -1
    auto.click(oneweek_btn)

    # 조회버튼
    search_btn = auto.get_element(By.ID, "submit_btn")
    if not search_btn:
        print("Error: Failed to find 조회 button")
        return -1
    auto.click(search_btn)

    buy_frame = auto.get_element(By.ID, "lottoBuyList")
    if not buy_frame:
        print("Error: Failed to find frame.")
        return -1

    with auto.get_frame(buy_frame):
        num_purchase = 0

        items = auto.get_elements(By.XPATH, "//html/body/table/tbody/tr")
        for item in items:
            columns = item.find_elements(By.XPATH, './/td')
            # 조회 결과가 하나도 없는 경우 처리
            if len(columns) == 1:
                # <td colspan="8" class="nodata">조회 결과가 없습니다.</td>
                break

            # 복권종류 확인
            if columns[1].text != lottery.value:
                continue

            # 미추첨 상태인지 확인
            if columns[5].text == '미추첨':
                num_purchase += int(columns[4].text)

        # 주당 구매 갯수와 현재 구매 개수를 비교
        return dh_get_maximum_purchase(lottery) - num_purchase


def dh_buy_lotto645(auto: Automatic, config):

    purchase_left = dh_get_num_of_purchase_left(auto, Lottery.lotto645)
    if purchase_left == -1:
        print("Error: Something went wrong.")
        return False

    number_per_purchase = min(
        purchase_left, config['lotto645_number_per_purchase'])

    if number_per_purchase == 0:
        print("Error: Purchase limit exceeded.")
        return False

    return lotto645_buy(auto, config['lotto645_numbers'],
                        number_per_purchase)
