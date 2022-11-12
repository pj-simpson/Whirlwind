from molotov import scenario


@scenario(weight=50)
async def scenario_one(session):
    async with session.get("http://localhost:8000/a") as resp:
        assert resp.status == 200


@scenario(weight=50)
async def scenario_two(session):
    async with session.get("http://localhost:8000/b") as resp:
        assert resp.status == 200
