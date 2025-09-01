from __future__ import annotations
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, DataTable, Button, Label
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from sqlmodel import select
from ..db import get_session
from ..models import Member, Filing, Trade, Signal

class SearchBar(Static):
    def compose(self) -> ComposeResult:
        yield Label("Search trader by name (type to filter):")
        yield Input(placeholder="e.g., Pelosi, Schumer, etc.", id="search_input")

class TraderList(Static):
    def __init__(self):
        super().__init__()
        self.table = DataTable(zebra_stripes=True)

    def compose(self) -> ComposeResult:
        yield self.table

    def populate(self, query: str = ""):
        self.table.clear(columns=True)
        self.table.add_columns("Member ID", "Name", "Chamber", "State", "Follow %")
        with get_session() as s:
            members = s.exec(select(Member)).all()
            for m in members:
                name = f"{m.first} {m.last}"
                if query and query.lower() not in name.lower():
                    continue
                self.table.add_row(m.member_id, name, m.chamber, m.state, f"{m.follow_score:.1f}")

class PortfolioView(Static):
    title = reactive("Portfolio")

    def __init__(self):
        super().__init__()
        self.table = DataTable(zebra_stripes=True)
        self.header = Label("Select a member to view portfolio.")

    def compose(self) -> ComposeResult:
        yield self.header
        yield self.table

    def show_member(self, member_id: str):
        with get_session() as s:
            m = s.get(Member, member_id)
            self.header.update(
                f"[b]{m.first} {m.last}[/] • {m.chamber.upper()} {m.state} • "
                f"Follow Likelihood: [b]{m.follow_score:.1f}%[/]"
            )
            self.table.clear(columns=True)
            self.table.add_columns("Issuer", "Ticker", "Txn Date", "Type", "Band", "Signal Score")
            filings = s.exec(select(Filing).where(Filing.filer_member_id == member_id)).all()
            for f in filings:
                trades = s.exec(select(Trade).where(Trade.filing_id == f.filing_id)).all()
                for t in trades:
                    sig = s.get(Signal, f"S-{t.trade_id}")
                    self.table.add_row(
                        t.issuer_raw,
                        t.ticker or "-",
                        t.txn_date.isoformat(),
                        t.txn_type or "-",
                        t.amount_band or "-",
                        f"{sig.score if sig else 0:.2f}",
                    )

class MenuApp(App):
    CSS = """
    Screen { layers: base; }
    #main { height: 1fr; }
    #left, #right { width: 1fr; height: 1fr; }
    #controls { height: auto; }
    """
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="main"):
            yield SearchBar()
            with Horizontal():
                self.traders = TraderList()
                self.portfolio = PortfolioView()
                yield self.traders
                yield self.portfolio
            with Horizontal(id="controls"):
                yield Button("View Today's Stats", id="stats_btn")
                yield Button("Exit", id="exit_btn", variant="error")
        yield Footer()

    def on_mount(self):
        self.query_one(Input).focus()
        self.traders.populate("")

    def on_input_changed(self, event: Input.Changed):
        self.traders.populate(event.value or "")

    def on_data_table_row_highlighted(self, message: DataTable.RowHighlighted):
        table = message.data_table
        if table is self.traders.table and table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            member_id = row[0]
            self.portfolio.show_member(member_id)

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "exit_btn":
            self.exit()
        elif event.button.id == "stats_btn":
            from ..stats import table_daily_report
            table = table_daily_report()
            self.push_screen(Static(str(table)))

def run_menu():
    app = MenuApp()
    app.run()
