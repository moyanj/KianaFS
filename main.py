import click
import multiprocessing


@click.group()
def cli():
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to listen on")
@click.option("--port", default=23901, type=int, help="Port to listen on")
def start(host, port):
    import uvicorn

    uvicorn.run("app:app", host=host, port=port, workers=multiprocessing.cpu_count())


@cli.command()
@click.argument("password")
def set_admin_password(password):
    import db
    import asyncio

    asyncio.run(db.init_db())
    asyncio.run(
        db.User.update_or_create(
            username="admin",
            defaults={"password": password},
        )
    )
    asyncio.run(db.Tortoise.close_connections())


if __name__ == "__main__":
    cli()
