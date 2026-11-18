// Optional managed preview launcher. The application itself is Python/Django.
import {spawn} from 'node:child_process';
const args = process.argv.slice(2);
const value = (flag, fallback) => args.includes(flag) ? args[args.indexOf(flag) + 1] : fallback;
const port = value('--port', process.env.PORT || '3000');
const host = value('--host', '127.0.0.1');
const child = spawn('.venv/bin/python', ['manage.py', 'runserver', `${host}:${port}`], {stdio:'inherit', env:process.env});
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
child.on('exit', code => process.exit(code || 0));
