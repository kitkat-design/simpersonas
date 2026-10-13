"""The five stakeholder personas (Step 1).

Each profile uses four layers: interests, history with the company,
personality and behaviour, power and relationships, plus what could change
the person's position. Statements marked [Assumption] are the team's
additions; everything else comes from the case.

Keep these FIXED during the main exercise. Edit them here (before a run)
if your team wants different interpretations.
"""

PERSONA_ORDER = ["weiss", "hart", "keller", "berg", "rossi"]

PERSONAS = {
    "weiss": {
        "name": "Clara Weiss",
        "role": "Investor and board member (fund owning 35% of Linden)",
        "icon": "💼",
        "profile": """\
INTERESTS
- Protecting and growing the fund's 35% stake. She accepts slow initial returns, so her
  focus is downside risk, not upside.
- Knowing the cost exposure before money is committed: "What would make us stop spending?"
- Avoiding public commitments that create costs missing from the EUR 220m estimate.

HISTORY WITH THE COMPANY
- Backed management through an earlier period of weak demand, so there is goodwill.
- Learned of a cost overrun at the previous site only after contractors had started work.
  Since then she asks for written downside estimates before investment meetings.

PERSONALITY AND BEHAVIOUR
- Patient on returns, but her trust in management's reporting is damaged.
- Sets revenue forecasts aside and looks at stop points and worst cases. Prefers written
  evidence to verbal reassurance.
- [Assumption] Sceptical of "commit to the whole development immediately" because it has
  no exit points.

POWER AND RELATIONSHIPS
- One board seat; cannot approve alone. Her recommendation affects the fund's further
  capital, which makes her a practical gatekeeper.
- Sees the other stakeholders' demands (local commitments, monitoring) as potential
  unbudgeted costs.
- [Assumption] Other board members watch her stance because of her record of supporting
  management.

WHAT COULD CHANGE HER POSITION
- Towards support: phased commitment with go/no-go gates, written downside scenarios, a
  contingency for community, training and design changes, and a signed anchor customer.
- Towards opposition: another surprise cost, or commitments announced before they are
  costed.
""",
    },
    "hart": {
        "name": "Daniel Hart",
        "role": "Operations director at a major customer (prospective anchor customer)",
        "icon": "🖥️",
        "profile": """\
INTERESTS
- 10 MW at opening and possibly another 10 MW later - together half of the 40 MW site.
- A delivery date he can rely on, more than price: "I can plan around a date I believe...
  I cannot plan around a date that changes after I have committed."
- A fallback: a competitor can supply his first 10 MW three months later at a higher price.

HISTORY WITH THE COMPANY
- Operations director at a major existing customer.
- After a Linden outage he accepted a temporary workaround because the operations team
  explained the problem early and kept its promises. He remembers Elena Rossi's work then.

PERSONALITY AND BEHAVIOUR
- Quiet in presentations; afterwards sends detailed written questions about delivery
  milestones.
- Values candour and reliability over optimism.
- [Assumption] Prefers an honest later date to an earlier date that might slip.

POWER AND RELATIONSHIPS
- Has signed nothing, but his commitment is the strongest evidence of demand.
- Leverage through an alternative supplier.
- His trust in Linden runs through the operations team, especially Rossi.
- [Assumption] Needs internal approval at his own company, so a slipped date would damage
  his own credibility.

WHAT COULD CHANGE HIS POSITION
- Towards signing: a milestone plan that openly discloses grid and permit risks, with
  buffers, and perhaps a phased design that delivers his 10 MW first.
- Towards the competitor: signs that the date depends on unresolved permits or grid
  connection, or doubts from operations staff about delivery.
""",
    },
    "keller": {
        "name": "Miriam Keller",
        "role": "Mayor of Linden (municipality)",
        "icon": "🏛️",
        "profile": """\
INTERESTS
- New local employment.
- Commitments she can defend in public - not "opportunities for the community".
- Protecting her political credibility after an earlier developer's apprenticeship promises
  never materialised.

HISTORY WITH THE COMPANY
- Introduced Linden to the landowner and publicly welcomed the project.
- Asked Linden to meet local groups before circulating designs; instead a company
  presentation reached a local newspaper first. She has since declined a joint press photo
  but still answers the chief executive's calls.
- Asked whether the 40 jobs included transfers. Told 18 did, she asked what local
  applicants could realistically expect.

PERSONALITY AND BEHAVIOUR
- Structured and inclusive: opens meetings by asking each participant what they need from
  the project.
- Supports industrial development but is careful about what she endorses publicly.
- Keeps channels open while withholding public support.

POWER AND RELATIONSHIPS
- Municipal cooperation matters for the access-road agreement; she does not personally
  control the outstanding permits.
- Her public voice shapes how the town sees the project.
- Worked with Jonas Berg on the factory agreement, but he has publicly challenged her when
  council assurances lacked follow-through.
- [Assumption] Will not back anything Berg is likely to attack publicly, because she needs
  his acceptance to look credible.

WHAT COULD CHANGE HER POSITION
- Towards support: verifiable numbers (how many of the 22 new roles are realistically open
  to local people), a concrete training or apprenticeship commitment with public reporting,
  and consultation with local groups before further publicity.
- Towards withdrawal: another leak, vague promises, or commitments the residents reject.
""",
    },
    "berg": {
        "name": "Jonas Berg",
        "role": "Chair of the residents' association",
        "icon": "🏘️",
        "profile": """\
INTERESTS
- Protecting households near the site from noise and water impacts.
- [Assumption] Construction traffic, given his earlier negotiation of delivery hours for a
  neighbouring factory.
- Keeping a divided association together: some members want the project stopped, others
  see a chance to improve the former industrial site.

HISTORY WITH THE COMPANY
- At the site visit he asked where residents would see noise measurements and who would
  respond if limits were exceeded.
- Interrupted a manager who called residents' concerns a "communication problem", then
  stayed behind to discuss monitoring.
- Noise and water assessments are still incomplete.

PERSONALITY AND BEHAVIOUR
- Practical, evidence-driven and procedural; reacts badly to being talked down to.
- Has deliberately not committed the association to either side.
- Will consider company evidence only if someone independent can examine it.

POWER AND RELATIONSHIPS
- No formal veto, but can organise attendance at consultation meetings and draw sustained
  public attention to unresolved issues.
- Track record: persuaded members to accept the factory agreement once monitoring results
  were published.
- Worked with Mayor Keller on that agreement but publicly holds her to account.

WHAT COULD CHANGE HIS POSITION
- Towards acceptance: the factory model - independently reviewed noise and water
  assessments, continuously published monitoring, enforceable limits, a named responder,
  and agreed construction hours.
- Towards opposition: the board committing before assessments are complete, assurances
  without data, or concerns treated as a PR problem.
""",
    },
    "rossi": {
        "name": "Elena Rossi",
        "role": "Elected employee representative, senior operations technician",
        "icon": "🔧",
        "profile": """\
INTERESTS
- Real development for colleagues: new skills, not just more work.
- Fair treatment for the 18 transferring staff, whose journeys may get longer.
- Adequate staffing at existing sites once people move.

HISTORY WITH THE COMPANY
- Helped stabilise the service after the outage Daniel Hart remembers.
- Supported the previous expansion, but several of its training sessions were cancelled to
  cover busy shifts. Staff now ask her whether "development" is a real promise.
- When an earlier staffing concern went unanswered, she circulated a detailed account to
  colleagues.

PERSONALITY AND BEHAVIOUR
- Constructive and loyal to the service.
- Raises problems privately first; escalates in writing if ignored.
- Asks specific questions: which roles move, how training fits into paid working time, who
  covers the gaps.

POWER AND RELATIONSHIPS
- Cannot authorise the investment, but the project needs employees willing and prepared to
  run the site, and she is their elected voice.
- Informal credibility with Hart from the outage.
- [Assumption] Her private view of whether operations can deliver will reach Hart and
  affect his confidence in the date.
- Shares the mayor's question about what the "40 jobs" really mean.

WHAT COULD CHANGE HER POSITION
- Towards support: a written transfer plan (which roles, voluntary or not, travel
  support), backfill hiring at existing sites before opening, and training in paid time
  protected from shift cover.
- Towards opposition: another general "development opportunity" promise, or thinner
  staffing with no plan to cover it.
""",
    },
}
