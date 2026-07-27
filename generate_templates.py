import json
import os

templates = [
    # Fresher
    {
        "id": "fresher-1",
        "name": "Eager Fresher",
        "category": "Fresher",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to express my strong interest in the {job_title} position at {company}. As a recent graduate, I am eager to contribute to a forward-thinking team. My academic background and hands-on projects have equipped me with a solid foundation in {skills}.\n\nThroughout my studies, I consistently demonstrated a passion for problem-solving and a dedication to achieving goals. I am confident that my enthusiasm and fresh perspective would make a positive impact at {company}.\n\nThank you for your time and consideration. I look forward to the possibility of discussing this exciting opportunity with you.\n\nSincerely,\n{name}"
    },
    {
        "id": "fresher-2",
        "name": "Motivated Graduate",
        "category": "Fresher",
        "tone": "semi-formal",
        "body": "Dear Hiring Team,\n\nI am thrilled to submit my application for the {job_title} role at {company}. Having recently completed my degree, I am eager to launch my career in a dynamic environment where I can apply my knowledge of {skills}.\n\nDuring my academic career, I developed a strong work ethic and the ability to learn quickly. The innovative approach of {company} greatly appeals to me, and I am excited about the opportunity to grow with your team.\n\nPlease find my attached resume for further details on my qualifications. Thank you for considering my application.\n\nBest regards,\n{name}"
    },
    {
        "id": "fresher-3",
        "name": "Academic Achiever",
        "category": "Fresher",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nPlease accept this letter as an expression of my interest in the {job_title} position at {company}. My recent academic accomplishments have provided me with a robust understanding of {skills}, preparing me well for this role.\n\nI am deeply impressed by {company}'s commitment to excellence and innovation in the industry. I am eager to bring my analytical mindset and dedication to your organization.\n\nI welcome the chance to discuss how my academic rigor and proactive approach align with your needs. Thank you for your review.\n\nSincerely,\n{name}"
    },

    # Experienced
    {
        "id": "experienced-1",
        "name": "Proven Professional",
        "category": "Experienced",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nWith a proven track record of success in enhancing operational efficiency and driving results, I am excited to apply for the {job_title} position at {company}. My extensive background in {skills} positions me to make an immediate impact on your team.\n\nIn my previous roles, I have consistently exceeded performance targets by leveraging my expertise to solve complex challenges. I admire {company}'s industry leadership and am eager to contribute my strategic insights to further your objectives.\n\nThank you for considering my application. I look forward to the opportunity to discuss my qualifications with you in detail.\n\nSincerely,\n{name}"
    },
    {
        "id": "experienced-2",
        "name": "Results-Driven Expert",
        "category": "Experienced",
        "tone": "formal",
        "body": "Dear Hiring Team,\n\nI am writing to apply for the {job_title} position at {company}. Over the course of my career, I have honed my expertise in {skills}, consistently delivering high-quality outcomes and exceeding expectations.\n\nMy professional journey has been defined by a commitment to continuous improvement and strategic execution. I am drawn to {company} because of your reputation for excellence, and I am eager to bring my results-driven approach to your organization.\n\nI appreciate your time and consideration and look forward to the possibility of an interview.\n\nBest regards,\n{name}"
    },
    {
        "id": "experienced-3",
        "name": "Strategic Leader",
        "category": "Experienced",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nAs an experienced professional with a strong background in {skills}, I am writing to express my interest in the {job_title} role at {company}. I have a history of successfully leading projects from conception to completion.\n\nI am particularly impressed by {company}'s strategic vision and recent market expansions. I am confident that my ability to navigate complex challenges and drive collaborative success aligns perfectly with your current needs.\n\nThank you for reviewing my application. I look forward to connecting soon.\n\nSincerely,\n{name}"
    },
    {
        "id": "experienced-4",
        "name": "Senior Specialist",
        "category": "Experienced",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to formally apply for the {job_title} position at {company}. With deep expertise encompassing {skills}, I have spent my career optimizing processes and delivering value.\n\nI understand that {company} is seeking an individual who can navigate nuanced operational demands while upholding high standards of quality. I am well-prepared to meet and exceed those expectations.\n\nI look forward to discussing how my extensive experience can benefit your team. Thank you for your time.\n\nSincerely,\n{name}"
    },

    # Career Change
    {
        "id": "career-change-1",
        "name": "Passionate Pivot",
        "category": "Career Change",
        "tone": "semi-formal",
        "body": "Dear Hiring Manager,\n\nI am excited to apply for the {job_title} position at {company}. While my previous professional background is in a different sector, my diverse experience has equipped me with highly transferable expertise in {skills}.\n\nI have long admired the work being done at {company} and have proactively sought to pivot my career toward this field. My unique perspective, combined with my eagerness to learn and adapt, makes me a strong candidate for this role.\n\nThank you for considering my varied background and the unique value I can bring to your team.\n\nSincerely,\n{name}"
    },
    {
        "id": "career-change-2",
        "name": "Transferable Skills",
        "category": "Career Change",
        "tone": "formal",
        "body": "Dear Hiring Team,\n\nI am writing to express my strong interest in the {job_title} role at {company}. I am currently transitioning careers and bring a proven track record of adaptability and core competencies in {skills}.\n\nMy decision to transition into this field is driven by a deep passion for your industry and a desire to contribute meaningfully to {company}'s mission. I am a quick and enthusiastic learner, ready to hit the ground running.\n\nI welcome the opportunity to discuss how my unconventional background is an asset for this position.\n\nBest regards,\n{name}"
    },

    # Internship
    {
        "id": "internship-1",
        "name": "Eager Intern",
        "category": "Internship",
        "tone": "semi-formal",
        "body": "Dear Hiring Manager,\n\nI am submitting my resume for consideration for the {job_title} internship at {company}. As a dedicated student with a keen interest in this field, I have built foundational knowledge in {skills}.\n\nAn internship with {company} represents an incredible opportunity to learn from industry leaders. I am highly motivated, detail-oriented, and ready to assist your team in any capacity needed.\n\nThank you for reviewing my application. I look forward to the possibility of contributing to your ongoing projects.\n\nSincerely,\n{name}"
    },
    {
        "id": "internship-2",
        "name": "Driven Student",
        "category": "Internship",
        "tone": "semi-formal",
        "body": "Dear Hiring Team,\n\nPlease accept my application for the {job_title} internship program at {company}. I am a hardworking student eager to apply my academic understanding of {skills} in a real-world setting.\n\nI have consistently sought out challenges that push me to grow, and {company}'s innovative environment is exactly where I hope to begin my professional journey. I am a proactive team player ready to tackle any task.\n\nI appreciate your time and consideration and hope to speak with you soon.\n\nBest regards,\n{name}"
    },
    {
        "id": "internship-3",
        "name": "Project-Focused",
        "category": "Internship",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to apply for the {job_title} internship position at {company}. Though early in my career journey, my academic projects have thoroughly immersed me in {skills}.\n\nI admire {company}'s commitment to fostering new talent and pushing technological boundaries. I am eager to bring my enthusiasm and strong foundational skills to your esteemed team.\n\nThank you for considering my application. I welcome the opportunity for an interview.\n\nSincerely,\n{name}"
    },

    # Remote
    {
        "id": "remote-1",
        "name": "Remote Pro",
        "category": "Remote",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to express my interest in the remote {job_title} position at {company}. I possess significant experience managing my own workload in a virtual environment while effectively utilizing {skills}.\n\nAs a self-starter, I thrive in remote settings, ensuring clear communication and consistent delivery of high-quality results. I am excited about the prospect of bringing my independent work ethic to {company}.\n\nThank you for your time and consideration. I look forward to discussing how I can contribute to your team from day one.\n\nSincerely,\n{name}"
    },
    {
        "id": "remote-2",
        "name": "Virtual Collaborator",
        "category": "Remote",
        "tone": "semi-formal",
        "body": "Dear Hiring Team,\n\nI am thrilled to apply for the remote {job_title} position at {company}. Having successfully navigated disparate, cross-functional teams, I excel in virtual collaboration and have robust abilities in {skills}.\n\nI am highly organized and proactive, ensuring that geographical distance never impedes project momentum. The dynamic culture of {company} is highly appealing to me, and I am eager to contribute remotely.\n\nI appreciate your consideration and hope to connect soon.\n\nBest regards,\n{name}"
    },
    {
        "id": "remote-3",
        "name": "Distributed Worker",
        "category": "Remote",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am applying for the remote {job_title} opportunity at {company}. I have a proven history of thriving in distributed teams, leveraging my proficiency in {skills} to drive successful outcomes regardless of location.\n\nEffective remote work requires exceptional communication and self-discipline, traits I bring to every role. I look forward to potentially contributing my strengths to {company}.\n\nThank you for reviewing my qualifications. I welcome the chance to discuss my fit for this role.\n\nSincerely,\n{name}"
    },

    # Creative
    {
        "id": "creative-1",
        "name": "Creative Spark",
        "category": "Creative",
        "tone": "creative",
        "body": "Hi there,\n\nI was immediately drawn to the {job_title} opening at {company}. As someone who constantly seeks out innovative solutions and creative approaches, I bring a unique blend of imagination and practical {skills} to the table.\n\nI believe that the best work happens when boundaries are pushed, and {company} clearly shares that philosophy. I am eager to infuse my creative energy into your upcoming projects and help bring bold ideas to life.\n\nI would love the opportunity to chat about how my creative vision aligns with your goals. Let's make something great together.\n\nBest,\n{name}"
    },
    {
        "id": "creative-2",
        "name": "Design Thinker",
        "category": "Creative",
        "tone": "creative",
        "body": "Dear Hiring Team,\n\nIf you are looking for someone who attacks challenges from unexpected angles, I am applying for the {job_title} role at {company}. My toolkit is built on strong {skills} and a passion for design thinking.\n\nI have followed {company}'s recent campaigns with great interest and am inspired by your aesthetic and vision. I am ready to jump in and bring compelling, fresh concepts to your team.\n\nThank you for the opportunity to present my application. I look forward to a potential collaboration.\n\nWarmly,\n{name}"
    },
    {
        "id": "creative-3",
        "name": "Visual Storyteller",
        "category": "Creative",
        "tone": "creative",
        "body": "Hello,\n\nWords and visuals have power, and as a candidate for the {job_title} position at {company}, I want to help you tell your story. With my background heavily rooted in {skills}, I specialize in crafting experiences that resonate.\n\n{company} stands out in the industry for its authentic voice, and I want to help amplify it. I am excited by the prospect of bringing my storytelling abilities to your creative team.\n\nLet's connect and discuss how we can create meaningful impact together. Thanks for your time.\n\nCheers,\n{name}"
    },

    # Tech
    {
        "id": "tech-1",
        "name": "Software Engineer",
        "category": "Tech",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to apply for the {job_title} position at {company}. With a solid foundation in computer science and extensive hands-on experience utilizing {skills}, I am a strong candidate for this technical role.\n\nI have successfully designed and deployed scalable solutions that improve system performance and user experience. The engineering culture at {company} is renowned, and I am eager to contribute clean, efficient code to your stack.\n\nThank you for considering my technical background. I look forward to further discussing my qualifications.\n\nSincerely,\n{name}"
    },
    {
        "id": "tech-2",
        "name": "Data Enthusiast",
        "category": "Tech",
        "tone": "semi-formal",
        "body": "Dear Hiring Team,\n\nI am thrilled to submit my interest in the {job_title} opportunity at {company}. My analytical mindset is complemented by my rigorous technical abilities in {skills}, enabling me to draw actionable insights from complex systems.\n\nI am deeply invested in solving challenging technical problems, a trait that clearly aligns with the mission of {company}. I am eager to bring my focused, data-driven approach to your development team.\n\nI appreciate your time reviewing my application and hope to speak soon.\n\nBest regards,\n{name}"
    },
    {
        "id": "tech-3",
        "name": "Systems Architect",
        "category": "Tech",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nPlease accept my application for the {job_title} vacancy at {company}. I specialize in building robust architectures and optimizing backend services, leveraging my deep proficiency in {skills}.\n\nIn our rapidly evolving digital landscape, I admire how {company} stays ahead of the technical curve. I am prepared to bring my strategic technical planning and execution skills to your team to drive continued innovation.\n\nThank you for your consideration. I welcome the opportunity to discuss my technical portfolio.\n\nSincerely,\n{name}"
    },
    {
        "id": "tech-4",
        "name": "Full Stack Dev",
        "category": "Tech",
        "tone": "semi-formal",
        "body": "Hi Hiring Team,\n\nI am excited to apply for the {job_title} role at {company}. As a full-stack professional, I bridge the gap between seamless user interfaces and powerful backends, relying heavily on my expertise in {skills}.\n\nI am passionate about building products that users love and codebases that developers enjoy maintaining. {company}'s commitment to excellent software engineering is why I am applying today.\n\nThanks for reviewing my details. I look forward to an opportunity to talk code with you.\n\nBest,\n{name}"
    },

    # Management
    {
        "id": "management-1",
        "name": "Team Leader",
        "category": "Management",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nI am writing to express my interest in the {job_title} position at {company}. Throughout my career in management, I have successfully driven team performance, consistently utilizing {skills} to exceed organizational goals.\n\nI pride myself on fostering inclusive, high-performing cultures that empower employees to do their best work. I am eager to bring my leadership experience to {company} to help guide your strategic initiatives forward.\n\nThank you for your time and consideration. I look forward to discussing my management philosophy with you.\n\nSincerely,\n{name}"
    },
    {
        "id": "management-2",
        "name": "Operations Manager",
        "category": "Management",
        "tone": "formal",
        "body": "Dear Hiring Team,\n\nI am applying for the {job_title} role at {company} to leverage my extensive background in operational oversight and strategic planning. My core competencies heavily feature {skills}, allowing me to optimize cross-functional workflows efficiently.\n\nI excel at identifying process bottlenecks and implementing targeted solutions. The trajectory of {company} is impressive, and I am keen to direct operations that will sustain your continued growth.\n\nI appreciate your review of my application and welcome an opportunity to interview.\n\nBest regards,\n{name}"
    },
    {
        "id": "management-3",
        "name": "Project Manager",
        "category": "Management",
        "tone": "formal",
        "body": "Dear Hiring Manager,\n\nPlease accept this letter as my formal application for the {job_title} position at {company}. As a dedicated project manager, my ability to deliver on time and under budget is supported by my strong use of {skills}.\n\nCoordinating multifaceted teams and navigating complex project requirements are where I thrive. I am very interested in bringing my structured execution and leadership capabilities to {company}.\n\nThank you for considering my credentials. I look forward to a potential discussion.\n\nSincerely,\n{name}"
    }
]

os.makedirs('data', exist_ok=True)
with open('data/templates.json', 'w') as f:
    json.dump(templates, f, indent=4)

print(f"Successfully generated {len(templates)} cover letter templates.")
