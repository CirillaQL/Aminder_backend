from fastapi import APIRouter, HTTPException
from modules.personas.schemas import PersonaCreateRequest, PersonaResponse, BigFiveProfileSchema
from modules.personas.personal import Person

router = APIRouter(prefix="/personas", tags=["personas"])

@router.post("/generate", response_model=PersonaResponse)
async def generate_persona(request: PersonaCreateRequest):
    """
    根据描述生成人格档案
    """
    try:
        person = Person(
            name=request.name,
            gender=request.gender,
            if_original=request.if_original
        )
        await person.init_big_five_profile(request.description)
        
        return PersonaResponse(
            name=person.name,
            gender=person.gender,
            personality=BigFiveProfileSchema(
                openness=person.personality.openness,
                conscientiousness=person.personality.conscientiousness,
                extraversion=person.personality.extraversion,
                agreeableness=person.personality.agreeableness,
                neuroticism=person.personality.neuroticism,
                traits=person.personality.traits
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
