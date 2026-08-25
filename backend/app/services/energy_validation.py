from app.services.energy_estimation import EnergyEstimationService

service = EnergyEstimationService()

# Solar Site
solar = service.estimate_energy(
    site_result={"site_id": 1},
    deployment_type="Solar",
    installed_capacity=100
)

# Wind Site
wind = service.estimate_energy(
    site_result={"site_id": 2},
    deployment_type="Wind",
    installed_capacity=100
)

# Hybrid Site
hybrid = service.estimate_energy(
    site_result={"site_id": 3},
    deployment_type="Hybrid",
    installed_capacity=100
)

print("Solar Site")
print(solar)

print("\nWind Site")
print(wind)

print("\nHybrid Site")
print(hybrid)