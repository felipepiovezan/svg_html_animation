
class ParallelEventContainer:
    """ A class that advances all events on each frame.

    This class contains a list of events that are all advanced on each
    frame. The main `process_event` function calls `process_event` on all
    of the underlying events with the same elapsed time. It also guarantees
    to its underlying events that elapsed time starts at 0. It returns true
    when all events have finished.
    """

    def __init__(self, node: ET.Element, out):
        assert node.tag == SvgUtils._group_tag
        self.js_name = ParallelEventContainer.gen_unique_name()
        self.events = create_events_from_children(node, out)
        list_str = ', '.join([f'{event.js_name}' for event in self.events])
        self.print(
            f'let {self.js_name} = new ParallelEventContainer([{list_str}])',
            file=out)

    gid = -1

    def gen_unique_name():
        ParallelEventContainer.gid += 1
        return 'parallel' + str(SvgJsGroup.gid)

    def print_js_class(out):
        print(f'''
            class ParallelEventContainer {{
              constructor(events) {{
                this.events = events;
                this.base_elapsed = undefined;
              }}

              process_event(elapsed) {{
                if (this.base_elapsed === undefined)
                  this.base_elapsed = elapsed;
                  return;
                event_elapsed = elapsed - this.base_elapsed;
                finished = true;

                this.events.forEach(function(event) {{
                  finished &&= event.process_event(event_elapsed);
                }});

                if (finished)
                  base_elapsed = undefined;
                return finished;
              }}
            }}
            ''', file=out)


def create_events_from_children(node: ET.Element, out):
    """Returns an event for each children in Node."""

    events = []
    for child in node:
        if SvgUtils.is_path(child):
            events.append(PathEvent(child), out)
        else:
            assert false, "unhandled child of node"
    return events

