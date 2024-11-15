# casualtyAllocator
 Project at AGI x SCSP

Working Project Summary:
Goal Project: AI Agent that military medical leader can use for prioritization strategy development

Inputs for AI:
casualties 
-each with chance of survival without care 
-required care (blood, time of medical personnel)
-chance of survival with required care

Resources:
Beds
Medical Personnel
Helicopter present
Equipment (can add more later)
-blood units

Actions:
Bed allocation
Helicopter allocation
Treatment/Medical Care allocation
Blood units


Outputs of AI:
Recommended Strategy: 
Patient in each bed/helicopter/
Which patients are you taking care of
(assume all or none survival)

Interface:
Terminal/CLI
Inputs Excel

Options:
Multi Agent RL
Q Learning
Cloud or Edge



Miscellaneous:
Reward calculation:
-maximize casualty survival
-reduced idle time
-transportation and equipment (helicopter full)


