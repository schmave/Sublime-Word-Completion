# Initial version from https://gist.github.com/skuroda/5105635
# Posted on SO: http://stackoverflow.com/questions/15260843

# Things still to do:
#   only complete unique (maybe make this an option? could be annoying with complete more)
#   complete from other open buffers, MRU first

import sublime
import sublime_plugin
import time

# The view that we searched in last
last_view = None
last_view_change_count = None  # the view's change count as of the last complete_word

# The location of the beginning of the prefix that was last searched for
last_initial_pos = None

# The prefix that was at last_initial_pos last time we searched
last_word_at_ipos = None

# The place to begin searching for words on next complete_word
last_search_pos = None

# True iff the most recent search was in the 'previous' direction
last_search_was_previous = None

# The location of the next text to copy for "complete more"
complete_more_pos = None

REGION_KEY = 'VimCompletion'
DRAW_FLAGS = sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE
MAX_SECONDS_TO_HIGHLIGHT = 3

# A dictionary from view ID to the time.time() stamp when a match was last
# underlined in it.
last_match_time_for_view = {}


def maybe_erase_regions(view):
    if view.id() not in last_match_time_for_view:
        return

    now = time.time()
    if now - last_match_time_for_view[view.id()] > MAX_SECONDS_TO_HIGHLIGHT:
        view.erase_regions(REGION_KEY)


def complete_word(view, edit, do_previous):
    global last_initial_pos, last_word_at_ipos, last_search_pos, last_view,\
           last_search_was_previous, complete_more_pos, last_view_change_count

    view.erase_regions(REGION_KEY)

    # Compute the region from the beginning of the word containing the cursor
    # through the cursor.
    initial_word_region = view.word(view.sel()[0])
    initial_word_region = sublime.Region(initial_word_region.begin(), view.sel()[0].begin())
    word = view.substr(initial_word_region)

    if (last_view == view and initial_word_region.begin() == last_initial_pos and
            last_word_at_ipos is not None and
            word.startswith(last_word_at_ipos) and last_search_pos is not None and
            view.change_count() == last_view_change_count):
        # Continue at previous search position with previous search prefix
        position = last_search_pos
        word = last_word_at_ipos

        if do_previous != last_search_was_previous:
            r = view.word(position + (1 if last_search_was_previous else -1))
            if do_previous:
                position = r.begin() - 1
            else:
                position = r.end() + 1
    else:
        # Start a new search
        if do_previous:
            position = initial_word_region.begin()
        else:
            position = initial_word_region.end()
        last_initial_pos = initial_word_region.begin()
        last_word_at_ipos = word
        last_view = view

    if (do_previous and position > 0) or (not do_previous and position < view.size()):
        position += -1 if do_previous else 1

    # sublime.status_message("word: %s; position: %d" % (word, position))

    match_found = False
    count = 0
    while not match_found and position >= 0 and position <= view.size() and count < 100000:
        count += 1
        compare_word_region = view.word(position)
        compare_word = view.substr(compare_word_region)

        # If we find a word that starts with the proper prefix, it's a match!
        # But don't count it if we have just found our starting place.
        num_chars_added = 0
        if (compare_word.startswith(word) and
                compare_word_region.begin() != view.word(view.sel()[0]).begin()):
            # underline the matched word for MAX_SECONDS_TO_HIGHLIGHT seconds
            view.add_regions(REGION_KEY, [compare_word_region], "error", "", DRAW_FLAGS)
            last_match_time_for_view[view.id()] = time.time()
            sublime.set_timeout(lambda: maybe_erase_regions(view),
                                MAX_SECONDS_TO_HIGHLIGHT * 1000 + 500)
            # replace word
            view.replace(edit, initial_word_region, compare_word)
            num_chars_added = compare_word_region.size() - initial_word_region.size()

            match_found = True

        adjustment = 0
        if position > initial_word_region.begin():
            adjustment = num_chars_added

        if do_previous:
            position = compare_word_region.begin() + adjustment - 1
        else:
            position = compare_word_region.end() + adjustment + 1
        complete_more_pos = compare_word_region.end() + adjustment

    if match_found:
        sublime.status_message(
            "Completion line: %s" %
            view.substr(view.line(sublime.Region(
                compare_word_region.begin(), compare_word_region.begin()))))
    else:
        sublime.status_message("No completion found")

    last_search_pos = position
    last_search_was_previous = do_previous
    last_view_change_count = view.change_count()


class CompletePreviousWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, True)


class CompleteNextWordCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        complete_word(self.view, edit, False)


class CompleteMoreCommand(sublime_plugin.TextCommand):
    def debug(self):
        classes = {
            sublime.CLASS_WORD_START: 'CLASS_WORD_START',
            sublime.CLASS_WORD_END: 'CLASS_WORD_END',
            sublime.CLASS_PUNCTUATION_START: 'CLASS_PUNCTUATION_START',
            sublime.CLASS_PUNCTUATION_END: 'CLASS_PUNCTUATION_END',
            sublime.CLASS_SUB_WORD_START: 'CLASS_SUB_WORD_START',
            sublime.CLASS_SUB_WORD_END: 'CLASS_SUB_WORD_END',
            sublime.CLASS_LINE_START: 'CLASS_LINE_START',
            sublime.CLASS_LINE_END: 'CLASS_LINE_END',
            sublime.CLASS_EMPTY_LINE: 'CLASS_EMPTY_LINE'
        }

        # for val in classes:
        #     print("%d %s" % (val, classes[val]))


        c = self.view.classify(self.view.sel()[0].begin())

        result = ''
        for val in classes:
            if val & c > 0:
                result += classes[val] + " "

        print("%d %s" % (c, result))


    def run(self, edit):
        # self.debug()
        # return

        global last_initial_pos, last_word_at_ipos, last_search_pos, last_view,\
                last_search_was_previous, complete_more_pos

        view = self.view

        # if last_initial_pos:
        #     print("starting complete more, last initial pos %d" % last_initial_pos)

        if not complete_more_pos:
            return

        last_initial_pos = last_word_at_ipos = last_search_pos = None
        last_view = last_search_was_previous = None

        cur_pos = view.sel()[0].begin()
        # print("character to right of complete_more_pos: %r, class %d" % (
        #     view.substr(complete_more_pos), view.classify(complete_more_pos)))

        # Copy to the end of the line or the end of the next word
        count = 0
        while (view.classify(complete_more_pos) & sublime.CLASS_LINE_END) == 0:
            count += 1
            view.insert(edit, cur_pos, view.substr(complete_more_pos))
            cur_pos += 1
            complete_more_pos += 1 if complete_more_pos < cur_pos else 2

            # max of 500 characters so that we don't loop forever due to an error
            if (count >= 500 or
                (view.classify(complete_more_pos) & sublime.CLASS_WORD_END)):
                break
