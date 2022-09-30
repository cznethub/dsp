---
name: Release checklist
about: Create a checklist for a release
title: ''
labels: ''
assignees: ''

---

- [ ] Code to release merged into develop for all deploy-able repos
   - [ ] dsp
   - [ ] dspfront
   - [ ] dspback 
- [ ] Develop deployed to alpha
- [ ] Developer (Unit) tests pass on alpha
- [ ] Functional (Selennium on-demand) tests pass on alpha
- [ ] RC branches created and deployed to beta
- [ ] Functional (Selennium on-demand) tests pass on beta
- [ ] Acceptance (manual System) tests pass
- [ ] RCs tagged as release and deployed to target
- [ ] Merge the release tag to master
- [ ] Merge master to develop
- [ ] Profit
