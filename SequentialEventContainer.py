class SequentialEventContainer:
    """ A class that one event on each frame.

    The main `process_event` function calls `process_event` on the first
    non-completed event of the container. It guarantees to its underlying
    events that elapsed time starts at 0. It returns true when all events have
    finished.
    """

    def __init__(self, events, out):
        """Construct a SequentialEventContainer from a list of Events."""

        self.js_name = SequentialEventContainer.gen_unique_name()
        list_str = ', '.join([f'{event.js_name}' for event in events])
        print(
            f'let {self.js_name} = new SequentialEventContainer([{list_str}])',
            file=out)

    def print_js_class(out):
        print(f'''
            class SequentialEventContainer {{
              constructor(events) {{
                this.events = events;
                this.base_elapsed = undefined;
                this.idx = 0;
              }}

              process_event(elapsed) {{
                if (this.base_elapsed === undefined)
                  this.base_elapsed = elapsed;

                if (this.idx < this.events.length) {{
                  event_elapsed = elapsed - this.base_elapsed;
                  finished = this.events[idx].process_event(event_elapsed);
                  if (finished) {{
                    this.base_elapsed = undefined;
                    this.idx++
                  }}
                }}

                if (this.idx >= this.events.length) {{
                  this.idx = 0;
                  return true;
                }}

                return false;
              }}
            }}''', file=out)

    gid = -1

    def gen_unique_name():
        SequentialEventContainer.gid += 1
        return 'seq' + str(SvgJsGroup.gid)
