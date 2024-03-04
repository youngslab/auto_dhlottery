import automatic as am
import automatic.selenium as s


class Lotto645(am.Automatic):
    def __init__(self, driver, max_num_of_games=5):
        self.__drv = driver
        self.__max_num_of_games = max_num_of_games
        # create context

        selenium = s.Context(self.__drv, timeout=10, differ=0)
        super().__init__([selenium])

    def login(self, id, pw):
        try:
            self.go(s.Url("로그인 페이지", 'https://dhlottery.co.kr/common.do?method=main'))
            self.click(s.Xpath("로그인링크", '//a[text()="로그인"]'))
            self.type(
                s.Xpath("PW 입력상자", '//input[@title="비밀번호"]', differ=1), pw)
            self.type(
                s.Xpath("ID 입력상자", '//input[@title="아이디"]', differ=1), id)
            self.click(
                s.Xpath("로그인 확인", '//div[@class="form"]/a[text()="로그인"]'))
            return True
        except Exception as e:
            print(f"로그인에 실패하였습니다. reason={e}")
            # Error: Failed to Login
            return False

    def get_num_of_purchases_in_this_week(self):
        try:
            self.go(
                s.Url("구매내역", "https://www.dhlottery.co.kr/myPage.do?method=lottoBuyListView"))
            self.click(
                s.Xpath("1주일", '//*[@id="frm"]/table/tbody/tr[3]/td/span[2]/a[2]'))
            self.click(s.Id("조회버튼", "submit_btn"))

            frame = s.Id("구매내역 프레임", "lottoBuyList")
            table = self.table(s.Xpath("구매내역", "//table", parent=frame))
            if table.empty:
                print("구매내역 테이블을 찾을 수 가 없습니다")
                return False

            table = table[(table['복권명'] == "로또6/45")
                          & (table['당첨결과'] == "미추첨")]

            return table["구입매수"].sum()

        except Exception as e:
            print(f"구매이력을 조회하는데 실패하였습니다. {e}")
            # Error: Failed to Login
            return -1

    def __buy_composite(self, game):
        fPanel = s.Id("프레임", 'ifrm_tab')
        self.click(s.Id("혼합선택", 'num1', parent=fPanel))
        for number in game:
            self.click(s.Xpath(
                f"숫자:{number}", f'//*[@id="checkNumGroup"]/label[{number}]', parent=fPanel))

        # 주어진 숫자의 개수가 부족하다면 자동선택
        if len(game) != 6:
            self.click(
                s.Xpath("자동선택", '//*[@id="checkNumGroup"]/div[1]/label', parent=fPanel))

        self.select(s.Id("적용수량", "amoundApply", parent=fPanel), "1")
        self.click(s.Id("확인버튼", "btnSelectNum", parent=fPanel))

    def buy(self, games):
        num_games = self.get_num_of_purchases_in_this_week()
        if num_games == -1:
            return

        num_games = self.__max_num_of_games - num_games
        if num_games <= 0:
            print(f"이미 가능한 모든 게임에 참여하였습니다.")
            return

        print(f"총 {num_games} 게임에 참가하겠습니다. games=[{games}]")
        try:
            self.go(
                s.Url("구매 페이지", "https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40"))
            for i in range(num_games):
                self.__buy_composite(games[i] if len(games) > i else [])

            # 구매하기 및 팝업 닫기
            fPanel = s.Id("프레임", 'ifrm_tab')
            self.click(s.Id("구매하기", 'btnBuy', parent=fPanel))
            self.click(s.Xpath(
                "팝업확인버튼", '//*[@id="popupLayerConfirm"]/div/div[2]/input[1]', parent=fPanel))
            self.click(s.Id("닫기버튼", 'closeLayer', parent=fPanel))

        except Exception as e:
            print(f"게임 구매하기를 실패하였습니다. reason={e}")
