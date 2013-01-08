from gevent.monkey import patch_all
patch_all()


from flask import Flask, render_template, url_for, redirect
from process import ProcessCapture, process_list
import traceback
import functools
import cjson as json
app = Flask('monitor')

process_monitors = {}

def debug_wrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            print traceback.print_exc()
            return build_error_page(traceback.format_exc())
    return wrapper

@app.route('/')
@debug_wrapper
def index():
    return redirect(url_for('processes'))

@app.route('/p/<pid>')
@debug_wrapper
def process(pid):
    if pid not in process_monitors:
        pm = ProcessCapture(pid)
        pm.start()
        process_monitors[pid] = pm
    return render_template('process.html', pm=process_monitors[pid], stats=process_monitors[pid].stats())

@app.route('/chart/<pid>/<var>')
@debug_wrapper
def chart(pid,var):
    return render_template('chart.html', pid=pid, var=var)
    

@app.route('/data/<pid>/<var>.json')
@debug_wrapper
def data(pid, var):
    from flask import make_response, Response
    resp = make_response(Response(),200)
    if pid not in process_monitors:
        pm = ProcessCapture(pid)
        pm.start()
        process_monitors[pid] = pm
    else:
        pm = process_monitors[pid]

    if not pm.values:
        process_monitors[pid] = pm
        pdata = {
            'min': 0,
            'max': 0,
            'values': [['Time', var]] + [[0,0]]
            }
    else:
        pm = process_monitors[pid]
        pdata = {
            'min': min(getattr(pm,var) or [0]),
            'max': max(getattr(pm,var) or [0]),
            'values': [['Time', var]] + [[i, getattr(pm,var)[i]] for i in xrange(pm.values)]
        }
    data =  json.encode(pdata)
    resp.data = data
    resp.headers['Content-Type'] = 'application/json'
    resp.headers['Content-Length'] = len(data)
    return resp

@app.route('/monitors')
@debug_wrapper
def monitors():
    fragments = []
    fragments.append("<h3> Running Monitors </h3>")
    fragments.append("<table>")
    for pid, pm in process_monitors.iteritems():
        fragments.append("<tr>")
        fragments.append("<td>%s</td>" % pid)
        fragments.append("<td>%s</td>" % pm.command)
        fragments.append("<td>Stop</td>")
        fragments.append("</tr>")
    fragments.append("</table>")
    return build_page("\n".join(fragments), title='Process Monitor')

@app.route('/stop/<pid>')
@debug_wrapper
def stop(pid):
    if pid in process_monitors:
        process_monitors[pid].stop()
        del process_monitors[pid]
    return render_template("success.html", message="Successfully stopped %s"%pid, url=url_for('monitors'))

@app.route('/processes')
@debug_wrapper
def processes():
    fragments = []
    fragments.append("""<h3> Running Processes </h3><hr>""")
    fragments.append("<table>")
    process_data = process_list()
    fragments.append("<tr>")
    for h in ["PID", "RSS", "%MEM", "%CPU", "COMMAND"]:
        fragments.append("<td>%s</td>" % h)
    fragments.append("</tr>")
    for i in xrange(len(process_data["PID"])):
        fragments.append("<tr>")
        for h in ["PID", "RSS", "%MEM", "%CPU", "COMMAND"]:
            if h == 'PID':
                fragments.append("<td><a href='%s'>%s</a></td>" % (url_for('process', pid=process_data['PID'][i]), process_data[h][i]))
            elif h == 'RSS':
                fragments.append("<td><a href='%s'>%s</a></td>" % (url_for('chart', pid=process_data['PID'][i], var='rss'), process_data[h][i]))
            elif h == '%CPU':
                fragments.append("<td><a href='%s'>%s</a></td>" % (url_for('chart', pid=process_data['PID'][i], var='cpu'), process_data[h][i]))
            elif h == '%MEM':
                fragments.append("<td><a href='%s'>%s</a></td>" % (url_for('chart', pid=process_data['PID'][i], var='mem'), process_data[h][i]))
            else:
                fragments.append("<td>%s</td>" % process_data[h][i])
        fragments.append("</tr>")
    fragments.append("</table>")
    return build_page("\n".join(fragments), title='Processes')
        
    
def build_error_page(msg):
    fragments = [
        "<h1>Error</h1>",
        "<p><pre>%s</pre></p>" % msg,
    ]
    content = "\n".join(fragments)
    return build_page(content)


def build_page(content, title=''):
    s = """<!DOCTYPE html>
<html>
<head><title>%s</title></head>
<body>
%s
</body>
</html>"""
    return s %(title, content)


if __name__ == '__main__':
    app.run()
