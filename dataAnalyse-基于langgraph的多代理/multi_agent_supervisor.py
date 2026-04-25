"""LangGraph multi-agent data-analysis demo.

The graph contains three workers:
- sqler: manages and queries a small sales database
- coder: runs lightweight Python analysis code
- chat: answers general questions directly

It is adapted from the original notebooks into a runnable Python module.
"""

from __future__ import annotations

import operator
import os
import random
from typing import Annotated, Literal, Sequence

from dotenv import load_dotenv
from faker import Faker
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine, func
from sqlalchemy.orm import declarative_base, sessionmaker
from typing_extensions import TypedDict


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sales_demo.db")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


class SalesData(Base):
    __tablename__ = "sales_data"

    sales_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product_information.product_id"))
    employee_id = Column(Integer)
    customer_id = Column(Integer, ForeignKey("customer_information.customer_id"))
    sale_date = Column(String(50))
    quantity = Column(Integer)
    amount = Column(Float)
    discount = Column(Float)


class CustomerInformation(Base):
    __tablename__ = "customer_information"

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(50))
    contact_info = Column(String(50))
    region = Column(String(50))
    customer_type = Column(String(50))


class ProductInformation(Base):
    __tablename__ = "product_information"

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(50))
    category = Column(String(50))
    unit_price = Column(Float)
    stock_level = Column(Integer)


class CompetitorAnalysis(Base):
    __tablename__ = "competitor_analysis"

    competitor_id = Column(Integer, primary_key=True)
    competitor_name = Column(String(50))
    region = Column(String(50))
    market_share = Column(Float)


def init_sample_database() -> None:
    """Create a small demo database when it is empty."""
    Base.metadata.create_all(engine)
    session = Session()
    try:
        if session.query(func.count(SalesData.sales_id)).scalar():
            return

        fake = Faker()
        for _ in range(50):
            session.add(
                CustomerInformation(
                    customer_name=fake.name(),
                    contact_info=fake.phone_number(),
                    region=fake.state(),
                    customer_type=random.choice(["Retail", "Wholesale"]),
                )
            )

        for _ in range(20):
            session.add(
                ProductInformation(
                    product_name=fake.word(),
                    category=random.choice(
                        ["Electronics", "Clothing", "Furniture", "Food", "Toys"]
                    ),
                    unit_price=random.uniform(10.0, 1000.0),
                    stock_level=random.randint(10, 100),
                )
            )

        for _ in range(10):
            session.add(
                CompetitorAnalysis(
                    competitor_name=fake.company(),
                    region=fake.state(),
                    market_share=random.uniform(0.01, 0.2),
                )
            )
        session.commit()

        for _ in range(100):
            session.add(
                SalesData(
                    product_id=random.randint(1, 20),
                    employee_id=random.randint(1, 10),
                    customer_id=random.randint(1, 50),
                    sale_date=fake.date_between(
                        start_date="-1y", end_date="today"
                    ).strftime("%Y-%m-%d"),
                    quantity=random.randint(1, 10),
                    amount=random.uniform(50.0, 5000.0),
                    discount=random.uniform(0.0, 0.15),
                )
            )
        session.commit()
    finally:
        session.close()


init_sample_database()


class AddSaleSchema(BaseModel):
    product_id: int
    employee_id: int
    customer_id: int
    sale_date: str
    quantity: int
    amount: float
    discount: float


class SaleIdSchema(BaseModel):
    sales_id: int


class UpdateSaleSchema(BaseModel):
    sales_id: int
    quantity: int
    amount: float


@tool(args_schema=AddSaleSchema)
def add_sale(product_id, employee_id, customer_id, sale_date, quantity, amount, discount):
    """Add a sale record to the demo database."""
    session = Session()
    try:
        sale = SalesData(
            product_id=product_id,
            employee_id=employee_id,
            customer_id=customer_id,
            sale_date=sale_date,
            quantity=quantity,
            amount=amount,
            discount=discount,
        )
        session.add(sale)
        session.commit()
        return {"sales_id": sale.sales_id, "message": "sale added"}
    finally:
        session.close()


@tool(args_schema=SaleIdSchema)
def delete_sale(sales_id):
    """Delete a sale record by sales_id."""
    session = Session()
    try:
        sale = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if not sale:
            return {"message": f"sale {sales_id} not found"}
        session.delete(sale)
        session.commit()
        return {"message": f"sale {sales_id} deleted"}
    finally:
        session.close()


@tool(args_schema=UpdateSaleSchema)
def update_sale(sales_id, quantity, amount):
    """Update quantity and amount for a sale record."""
    session = Session()
    try:
        sale = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if not sale:
            return {"message": f"sale {sales_id} not found"}
        sale.quantity = quantity
        sale.amount = amount
        session.commit()
        return {"message": f"sale {sales_id} updated"}
    finally:
        session.close()


@tool(args_schema=SaleIdSchema)
def query_sale(sales_id):
    """Query one sale record by sales_id."""
    session = Session()
    try:
        sale = session.query(SalesData).filter(SalesData.sales_id == sales_id).first()
        if not sale:
            return {"message": f"sale {sales_id} not found"}
        return {
            "sales_id": sale.sales_id,
            "product_id": sale.product_id,
            "employee_id": sale.employee_id,
            "customer_id": sale.customer_id,
            "sale_date": sale.sale_date,
            "quantity": sale.quantity,
            "amount": sale.amount,
            "discount": sale.discount,
        }
    finally:
        session.close()


@tool
def top_sales(limit: int = 5):
    """Return top sales records ordered by amount."""
    session = Session()
    try:
        rows = (
            session.query(SalesData)
            .order_by(SalesData.amount.desc())
            .limit(max(1, min(limit, 20)))
            .all()
        )
        return [
            {
                "sales_id": row.sales_id,
                "product_id": row.product_id,
                "quantity": row.quantity,
                "amount": round(row.amount, 2),
                "sale_date": row.sale_date,
            }
            for row in rows
        ]
    finally:
        session.close()


repl = PythonREPL()


@tool
def python_repl(code: Annotated[str, "Python code to execute for analysis."]):
    """Run Python code for calculations or simple analysis."""
    try:
        result = repl.run(code)
    except BaseException as exc:
        return f"Failed to execute. Error: {exc!r}"
    return f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"


def build_llm(model_env: str, default_model: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv(model_env, default_model),
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY", "not-set"),
    )


llm = build_llm("MODEL_NAME", "qwen3-max")
coder_llm = build_llm("CODER_MODEL_NAME", "qwen-coder-turbo")

db_agent = create_agent(
    model=llm,
    tools=[add_sale, delete_sale, update_sale, query_sale, top_sales],
    system_prompt=(
        "You are a database manager. Use the sales database tools to answer data "
        "questions accurately. Return concise Chinese explanations."
    ),
)

code_agent = create_agent(
    model=coder_llm,
    tools=[python_repl],
    system_prompt=(
        "You are a Python analyst. Use Python only when calculation or data "
        "transformation is needed. Return concise Chinese explanations."
    ),
)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str


def db_node(state: AgentState):
    result = db_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="sqler")]}


def code_node(state: AgentState):
    result = code_agent.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=result["messages"][-1].content, name="coder")]}


def chat_node(state: AgentState):
    response = llm.invoke(state["messages"])
    return {"messages": [AIMessage(content=response.content, name="chat")]}


members = ["chat", "coder", "sqler"]
options = members + ["FINISH"]


class Router(TypedDict):
    next: Literal["chat", "coder", "sqler", "FINISH"]


def supervisor(state: AgentState):
    system_prompt = (
        "You are a supervisor managing three workers: chat, coder, sqler.\n"
        "- chat: answer general questions directly.\n"
        "- coder: run Python for calculations or analysis.\n"
        "- sqler: query or modify the sales database.\n"
        "Choose the next worker. If the task is complete, choose FINISH."
    )
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    response = llm.with_structured_output(Router).invoke(messages)
    return {"next": response["next"]}


workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor)
workflow.add_node("sqler", db_node)
workflow.add_node("coder", code_node)
workflow.add_node("chat", chat_node)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {"chat": "chat", "coder": "coder", "sqler": "sqler", "FINISH": END},
)
for member in members:
    workflow.add_edge(member, "supervisor")

graph = workflow.compile()


def main() -> None:
    query = input("请输入数据分析问题：").strip()
    if not query:
        print("问题不能为空。")
        return
    for chunk in graph.stream(
        {"messages": [HumanMessage(content=query)]},
        {"recursion_limit": 20},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
