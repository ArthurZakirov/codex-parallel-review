# Developing Parallel Review hooks

When editing hook Python or prompts, run `./develop` from the worktree you will edit. The installed entry point uses that checkout on the next event in this Codex thread. Other threads retain their own selections. A shell edit, an agent patch and an editor save all take effect the same way.

Use a new user turn to observe submission-prompt changes. Use a reviewable edit to observe reviewer or handoff changes. Run `./develop --off` before removing the worktree, or select another worktree from the same chat.

Install the version containing the development entry point once. Test changes to the entry point, event registrations, matchers or plugin metadata in an isolated installation. Those changes affect the installed registration and may require renewed trust.
