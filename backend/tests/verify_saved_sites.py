import os
import sys
from app.database.database import Base, engine, SessionLocal
from app.models.saved_site import SavedSite
from app.schemas.saved_site import SavedSiteCreate

def verify():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Test saving site for team ORG-1001
    test_org = "ORG-1001"
    new_site = SavedSite(
        organization_id=test_org,
        name="Bhadla Solar Park Test",
        description="Desert solar parcel test",
        latitude=27.5397,
        longitude=71.9152,
        status="APPROVED",
        score=94.5
    )
    db.add(new_site)
    db.commit()
    db.refresh(new_site)
    
    print(f"SUCCESS: Inserted SavedSite id={new_site.id} for team {new_site.organization_id}")
    
    # Query back
    sites = db.query(SavedSite).filter(SavedSite.organization_id == test_org).all()
    print(f"SUCCESS: Query returned {len(sites)} sites for team {test_org}")
    
    # Clean up test site
    db.delete(new_site)
    db.commit()
    print("SUCCESS: Cleaned up test record cleanly.")
    db.close()

if __name__ == "__main__":
    verify()
