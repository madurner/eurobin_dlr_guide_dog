# meeting notes 13.01

### Leo, Felix, Anne, Seth

In sum:
At first glance no dealbreaker for project, contact IT for detailed concept & feasible implementation.

#### running project: InsectVision

current contact person: Wolfgang Stürzle
but implementation & setup from Elma

- time until online ~6 months, hosted with DMZ (not cheap: 5-10€ per month)
- no export control since programm itself not accessible
- runs on webserver, no root access simple virtual server

#### proposed setups

Our pipeline runs on an external computer (not in Institutsnetz) either physically here at DLR or on a Webserver.

possible hosts:

- DMZ
    - very expensive
    - uses reverse proxy for internet access
    - sounded like more DLR bureaucracy
- IONOS
    - GPUs available
    - contact from other institute @Arne Bachmann (IT manager SL Hamburg)
    - scalability might be easier
    - hosting on webserver means no cissy / conan environments which means more integration work than expected
    - updating the webserver could be implemented using cron jobs syncing with the artifactory server

Software stack:
personal preference python (Seth), but everything works in the end.

#### contact persons

- SvD: could have a good concept/implementation idea for us
- H-J: takes time for these IT projects
- SE: our IT Security expert. Should be able to support us with e.g. authentication and security.

#### Next steps

- [ ] Contact H-J and get his opinion
