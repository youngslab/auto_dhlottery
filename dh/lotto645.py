
from integ_auto import *

# 구매 page내에 있어야 한다.


def lotto645_buy_my_number(auto: Automatic):
    ifrm_tab = auto.get_element(By.XPATH, '//iframe[@id="ifrm_tab"]')
    if not ifrm_tab:
        print("Error: Failed to find iframe")
        return False

    with auto.get_frame(ifrm_tab):
        my_numbers_btn = auto.get_element(
            By.XPATH, '//*[@id="num4"]')
        auto.click(my_numbers_btn)

        my_number = auto.get_element(
            By.XPATH, '//*[@id="myList"]/li/input')
        auto.click(my_number)

        confirm_btn = auto.get_element(
            By.XPATH, '//*[@id="divWay2Buy3"]/div[2]/input[1]')
        auto.click(confirm_btn)


def lotto645_buy_composite(auto: Automatic, numbers, count):
    ifrm_tab = auto.get_element(By.XPATH, '//iframe[@id="ifrm_tab"]')
    if not ifrm_tab:
        print("Error: Failed to find iframe")
        return False

    with auto.get_frame(ifrm_tab):
        my_numbers_btn = auto.get_element(
            By.XPATH, '//*[@id="num1"]')
        auto.click(my_numbers_btn)

        for number in numbers:
            number_label = auto.get_element(
                By.XPATH, f'//*[@id="checkNumGroup"]/label[{number}]')
            auto.click(number_label)

        # 자동선택
        if len(numbers) != 6:
            auto_select = auto.get_element(
                By.XPATH, '//*[@id="checkNumGroup"]/div[1]/label')
            auto.click(auto_select)

        select = auto.get_element(By.ID, 'amoundApply')
        auto.select(select, f'{count}')

        confirm_btn = auto.get_element(By.ID, 'btnSelectNum')
        confirm_btn.click()


def lotto645_buy_random(auto: Automatic, count):
    ifrm_tab = auto.get_element(By.XPATH, '//iframe[@id="ifrm_tab"]')
    if not ifrm_tab:
        print("Error: Failed to find iframe")
        return False

    with auto.get_frame(ifrm_tab):
        my_numbers_btn = auto.get_element(
            By.XPATH, '//*[@id="num2"]')
        auto.click(my_numbers_btn)

        select = auto.get_element(By.ID, 'amoundApply')
        auto.select(select, f'{count}')

        confirm_btn = auto.get_element(By.ID, 'btnSelectNum')
        confirm_btn.click()


def lotto645_buy(auto: Automatic, numbers, total_count):
    if total_count > 5:
        return False

    auto.go('https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40')

    for number in numbers:
        lotto645_buy_composite(auto, number, 1)

    # random
    lotto645_buy_composite(auto, [], total_count - len(numbers))

    # 확인 및 팝업 닫기
    ifrm_tab = auto.get_element(By.XPATH, '//iframe[@id="ifrm_tab"]')
    if not ifrm_tab:
        print("Error: Failed to find iframe")
        return False

    with auto.get_frame(ifrm_tab):
        buy_btn = auto.get_element(By.ID, 'btnBuy')
        auto.click(buy_btn)

        confirm_btn = auto.get_element(
            By.XPATH, '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]')
        auto.click(confirm_btn)

        close_btn = auto.get_element(By.ID, 'closeLayer')
        auto.click(close_btn)

    return True
