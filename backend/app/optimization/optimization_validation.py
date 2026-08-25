from app.optimization.optimizer import DeploymentOptimizer

optimizer = DeploymentOptimizer()

sites = [

    {
        "name": "Site 1",
        "solar_score": 90,
        "wind_score": 85,
        "land_area": 120,
        "resource_score": 90,
        "available_land_percent": 60
    },

    {
        "name": "Site 2",
        "solar_score": 85,
        "wind_score": 40,
        "land_area": 70,
        "resource_score": 70,
        "available_land_percent": 30
    },

    {
        "name": "Site 3",
        "solar_score": 40,
        "wind_score": 88,
        "land_area": 25,
        "resource_score": 45,
        "available_land_percent": 10
    }

]

for site in sites:

    result = optimizer.generate_deployment_plan(
        solar_score=site["solar_score"],
        wind_score=site["wind_score"],
        land_area=site["land_area"],
        resource_score=site["resource_score"],
        available_land_percent=site["available_land_percent"]
    )

    print("\n", site["name"])
    print(result)