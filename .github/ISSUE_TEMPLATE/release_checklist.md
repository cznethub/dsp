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
- [ ] Developer tests pass on alpha
- [ ] RC branches created and deployed to beta
- [ ] Functional tests pass on beta
- [ ] RCs tagged as release and deployed to target
- [ ] Acceptance tests pass
- [ ] Merge the release tag to master
- [ ] Merge master to develop
- [ ] Profit
