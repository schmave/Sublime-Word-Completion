# Word Completion for Sublime Text 3
Vim-style word completion for Sublime Text 3. This plugin provides commands to complete the word or line you are typing based on other text in the current buffer. It is similar to [Vim's word completion commands](http://vim.wikia.com/wiki/Any_word_completion) bound to Ctrl-N and Ctrl-P.

## How to use

Type the beginning of a word, then press ctrl+9 -- it will search previous words in the file to complete the current word. Keep pressing ctrl+9 to keep searching earlier in the file. The matching word is underline and the matching line is shown in the status bar.

After a match is found, you can press ctrl+space to complete more words from the matched line. Each time you press ctrl+space, text is copied to the end of the next word or the end of the line, whichever comes first.

## How to install

Install this plugin with the excellent [Package Control](https://packagecontrol.io/) system. Then add the keybindings for the following commands, like so:


    { "keys": ["ctrl+9"], "command": "complete_previous_word"},
    { "keys": ["ctrl+0"], "command": "complete_next_word"},
    { "keys": ["ctrl+space"], "command": "complete_more"},


### Installing the hard way

Download the code from github, move the entire folder into ~/Library/Application
Support/Sublime Text 3/Packages/, and setup the keybindings from above.
