from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pandas import DataFrame
from prettytable import PrettyTable


def dataframe_to_prettytable(df: DataFrame) -> PrettyTable:
    """Convert a pandas DataFrame to a PrettyTable object."""
    pt = PrettyTable()
    pt.field_names = df.columns.tolist()
    pt.add_rows(df.values.tolist())
    return pt


class SlackReporter:
    def __init__(self, slack_token: str, channel: str):
        """Initialize the SlackReporter with a token and channel name."""
        self.client = WebClient(token=slack_token)
        self.channel = channel

    def send_message(self, message: str) -> bool:
        """Send a simple text message to the Slack channel."""
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message
            )
            return response["ok"]
        except SlackApiError as e:
            error = e.response.get('error', 'Unknown error')
            print(f"Error sending message to {self.channel}: {error}")
            return False

    def send_dataframe(self, df: DataFrame) -> bool:
        """Send a DataFrame as a PrettyTable string to the Slack channel."""
        try:
            table_str = str(dataframe_to_prettytable(df))
            return self.send_message(table_str)
        except Exception as e:
            print(f"Error converting DataFrame to table: {e}")
            return False
