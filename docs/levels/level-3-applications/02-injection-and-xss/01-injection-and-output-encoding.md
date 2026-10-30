---
title: "Injection, Contexts and Encoding"
description: "SQL injection, command injection and the three XSS types, taught as one idea: data crossing into an interpreter."
module_code: CYB-302
level: 3
kind: lesson
prerequisites: [CYB-301]
estimated_minutes: 360
difficulty: intermediate
safety: isolated-vm
lab_ids: [LAB-302-01, LAB-302-02]
assessment: knowledge-check
version: 1.0.0
last_reviewed: 2026-10-29
reviewers: []
status: published
tags: [sql-injection, xss, command-injection, output-encoding, csp]
---

# Injection, Contexts and Encoding

**Level 3** · 360 minutes · **Prerequisites:** CYB-301 · **Labs:**
[SQL Injection and Its Fix](lab-01-sql-injection.md) ·
[Reflected and Stored XSS](lab-02-xss.md)

## Why this matters

A single quote in a form field should be a character. When it is not — when it closes a string literal and the
rest of the input is parsed as SQL — an application that was supposed to answer one question can be made to
answer any question its database user is allowed to ask. The same logic applies to `<` in HTML, `;` in a shell,
and `{{` in a template.

Injection remains [A05:2025](https://owasp.org/Top10/2025/) because the fix is architectural, not a filter you
add at the end. Testers who understand the mechanism find injection that scanners miss; developers who
understand it stop reintroducing it.

## Learning outcomes

By the end of this lesson you will be able to:

- Explain why interpolation into an interpreter creates a vulnerability, using the query parser as the example.
- Distinguish error-based, boolean-based, union-based and time-based SQL injection techniques by what they
  require and what they reveal.
- Rewrite a vulnerable query using parameter binding and explain the mechanism that makes it safe.
- Classify an XSS by context (HTML, attribute, URL, script, DOM) and select the correct encoding for it.
- Explain why input filtering is not the primary control for XSS, and what is.

## Prerequisites and setup

- Web lab running; DVWA security level **Low**.
- `sqlite3` CLI and Python 3.10+ with `flask` in a virtual environment.
- Your annotated exchange table from [LAB-301-02](../01-web-architecture-and-http/lab-02-intercept-a-session.md),
  which tells you which parameters exist.

---

## Core concepts

### 1. The one bug, stated once

Every injection flaw has the same shape:

```text
interpreter( "fixed text" + user_data )
```

The interpreter cannot tell which characters came from the template and which came from the user. If the user
supplies a character that is meaningful to the interpreter, the structure of the command changes.

```python
# VULNERABLE — the user's text becomes part of the query's syntax
query = "SELECT id, name FROM products WHERE name = '" + user_input + "'"
cursor.execute(query)
```

With `user_input = "x' OR '1'='1"` the database receives:

```sql
SELECT id, name FROM products WHERE name = 'x' OR '1'='1'
```

A `WHERE` clause intended to return one row now returns all of them. The application did nothing wrong with the
result — it displayed what the query returned. The vulnerability is entirely in how the query was built.

The correct construction sends the **text of the query** and the **data** as separate items:

```python
# SAFE — data is bound to a placeholder and never parsed as SQL
query = "SELECT id, name FROM products WHERE name = ?"
cursor.execute(query, (user_input,))
```

**Why this actually works** — not "because it escapes quotes". With a parameterised statement the database
prepares the query plan first, with the structure fixed, then supplies the value as a typed datum to that plan.
There is no point at which the value is scanned for SQL syntax. A quote inside the value is just a quote in a
string. This is why parameter binding survives every encoding trick: there is nothing to bypass.

Placeholder syntax by driver, because this is where people go wrong when porting:

| Stack | Placeholder | Note |
| --- | --- | --- |
| Python `sqlite3` | `?` | Also `:name` for named parameters |
| Python `psycopg` (PostgreSQL) | `%s` | Not a format string — the driver substitutes |
| Node `pg` | `$1`, `$2` | Positional, numbered |
| Java JDBC | `?` | `PreparedStatement` |
| PHP PDO | `:name` or `?` | Must disable emulated prepares for real server-side binding |

Three places parameterisation silently fails, all of which you will meet in code review:

1. **Identifiers cannot be parameters.** `ORDER BY ?` does not work. A column name or table name must be
   selected from an allowlist, then interpolated. This is the most common excuse for string concatenation.
2. **`IN` lists need generated placeholders.** `WHERE id IN (?)` binds one value. Build `(?,?,?)` from the list
   length — the placeholders are code, the values are data.
3. **ORMs have escape hatches.** `Raw()`, `.whereRaw()`, `text()` and string-built `filter()` calls put you back
   in the concatenation business. Review them by name.

### 2. SQL injection: four techniques, one flaw

You do not need to memorise payload lists. You need to know what each technique requires, because that tells you
what the application exposes.

| Technique | Requires | What it reveals | Detectable by |
| --- | --- | --- | --- |
| Error-based | Verbose database errors reaching the client | Schema names, query structure, sometimes data | A single malformed input |
| Boolean-based | A response that differs between true and false | One bit per request — data extracted slowly | Careful comparison of responses |
| Union-based | Matching column count and compatible types | Arbitrary rows from other tables in one request | Fast, obvious once it works |
| Time-based (blind) | Ability to make the database wait | One bit per request, no output needed | Response timing |

Start with the cheapest test in every case: **send a single quote and a comment marker, and compare the response
to the unmodified request.** A `500`, a different error page, or a changed body means the input reached the
parser. A normal page means it did not — or that errors are suppressed, which is why the comparison matters more
than the status code.

A note on comment syntax, because it trips people up across engines: MySQL accepts `-- ` (dash-dash-space),
`#`, and `/* */`; PostgreSQL and SQLite accept `--` and `/* */` but not `#`; SQL Server accepts `--` and
`/* */`. A payload that "doesn't work" is often a comment-syntax mismatch, not a missing vulnerability.

**What injection actually costs.** Reading one extra table is the demonstration. The impact statement in a
report is about what the *database user* can do: read every table in the schema, modify or delete rows, sometimes
read files or execute operating-system commands through database features. Least-privilege database accounts
limit the blast radius; they do not fix the flaw.

### 3. Command injection and other interpreters

The same shape appears wherever an application shells out:

```python
# VULNERABLE
os.system("ping -c 1 " + host)
```

`host = "192.0.2.30; id"` runs two commands. The fix is not to strip semicolons — it is to not use a shell:

```python
# SAFE — no shell, arguments passed as a list
subprocess.run(["ping", "-c", "1", host], check=True, timeout=5)
```

And a second control that is often skipped: **validate the value's shape** before using it. A host must match an
IP-address or hostname pattern; a filename must not contain path separators; a quantity must be an integer in
range. Shape validation is not a substitute for safe APIs, but it turns "any string reaches the interpreter" into
"only strings that look like the expected thing do".

Other members of the family, mapped so you recognise them:

| Interpreter | Where it appears | Safe construction |
| --- | --- | --- |
| SQL | Query strings, ORM raw fragments | Parameter binding |
| OS shell | `system()`, backticks, `child_process.exec` | Argument arrays, no shell |
| Template engine | User-controlled template source | Never compile user input as a template |
| LDAP | Directory filters | Escape filter metacharacters, use the library's encoder |
| XPath | XML queries | Parameterised XPath API |
| Expression languages | SpEL, OGNL, Jinja `eval` | Do not evaluate user input |
| Deserialisation | `pickle`, Java serialisation, YAML `load` | Typed formats, allowlists, safe loaders |

### 4. XSS: the same bug in a browser

XSS is injection into an HTML document. The interpreter is the browser's parser, and the "query" is the page.

Three types, distinguished by *where the payload lives* and *where it executes*:

| Type | Payload arrives via | Persists? | Executes in | Typical source |
| --- | --- | --- | --- | --- |
| Reflected | The current request (query string, form field) | No | Victim's browser, page that echoed it | Search results, error messages, redirects |
| Stored | Data saved by the application | Yes, until deleted | Every visitor's browser | Comments, profiles, support tickets, filenames |
| DOM-based | Client-side script reading a source and writing to a sink | No | Victim's browser, entirely client-side | `location.hash`, `innerHTML` |

Stored XSS is the serious one in assessments: no interaction is needed beyond viewing a page, so one submission
affects every user who sees it — including administrators. Reflected XSS needs a crafted link. DOM XSS is
invisible to the server, so no server-side filter or WAF will ever see it.

**The context decides the encoding.** This is the part beginners skip, and it is the reason "escape the input"
fails:

```html
<!-- HTML body: encode & < > " ' -->
<p>Hello, <?= h(name) ?></p>

<!-- Attribute value: same encoding, and ALWAYS quote the attribute -->
<input value="<?= h(name) ?>">

<!-- URL attribute: URL-encode, then HTML-encode the whole thing -->
<a href="/search?q=<?= h(urlencode(q)) ?>">…</a>

<!-- Inside a <script> block: HTML encoding does nothing; use JSON encoding -->
<script>const cfg = <?= json_encode(cfg, JSON_HEX_TAG|JSON_HEX_AMP) ?>;</script>
```

Encoding is applied **on output, at the point of use** — not on input, and not once at the edge. Storing raw
data is correct; encoding it before storage corrupts it and still leaves every non-HTML consumer (JSON APIs,
logs, emails) unencoded.

**Where filters fail.** Blocking `<script>` is defeated by `<img src=x onerror=…>`, `<svg onload=…>`, and a
hundred other elements. Stripping `on\w+` is defeated by encoding, casing, and mutation XSS. This is why the
control is *output encoding plus a restrictive CSP*, with HTML sanitisation only where rich text is a genuine
requirement — and then via a maintained library (DOMPurify) with an allowlist, never a regex.

**DOM XSS deserves its own rule:** identify sources and sinks.

```javascript
// VULNERABLE — the fragment is attacker-controlled and written as HTML
document.getElementById('out').innerHTML = decodeURIComponent(location.hash.slice(1));
```

Sources: `location`, `document.URL`, `document.referrer`, `postMessage` data, `localStorage`.
Sinks: `innerHTML`, `outerHTML`, `document.write`, `eval`, `setTimeout(string)`, `jQuery.html()`.
The fix is `textContent` for text, and a sanitiser for the rare case where HTML is required.

### 5. CSP: what it buys and what it does not

`Content-Security-Policy` restricts where the browser will load and execute code from. It is the control that
limits the *impact* of an XSS you failed to prevent, and it is the one header most often deployed in a useless
form.

| Policy | Effect |
| --- | --- |
| `default-src 'self'` | Baseline: no third-party origins by default |
| `script-src 'nonce-r4nd0m' 'strict-dynamic'` | Only scripts carrying the per-request nonce run; nonces are unguessable |
| `script-src 'unsafe-inline'` | Inline scripts allowed — **negates the main protection** |
| `script-src 'self' https:` | Any script on any HTTPS origin — weak |
| `object-src 'none'`, `base-uri 'self'` | Closes plugin and `<base>` injection |
| `frame-ancestors 'none'` | Clickjacking control (replaces `X-Frame-Options`) |
| `report-only` | Reports violations without blocking — a migration step, not a control |

The test that matters in an assessment: **would this policy have blocked the payload I just executed?** If the
answer is no, report the policy as ineffective. If yes, report it as a compensating control and still report the
XSS.

---

## Worked example: from payload to patch

DVWA's SQL injection module, security level Low, takes a numeric `id` and returns a row. The vulnerable code is
the classic concatenation:

```php
$id = $_GET['id'];
$getid = "SELECT first_name, last_name FROM users WHERE user_id = '$id'";
$result = mysqli_query($connection, $getid);
```

**Step 1 — confirm the input reaches the parser.** Send a quote and compare.

```bash
curl -sS -o /tmp/base.html "http://192.0.2.30:4280/vulnerabilities/sqli/?id=1&Submit=Submit" \
  -b evidence/dvwa.jar
curl -sS -o /tmp/quote.html "http://192.0.2.30:4280/vulnerabilities/sqli/?id=1'&Submit=Submit" \
  -b evidence/dvwa.jar
diff <(grep -o 'First name.*' /tmp/base.html) <(grep -o 'First name.*' /tmp/quote.html) && echo "no difference"
```

**Expected:** the quote request produces a database error or a visibly different body. That difference is the
finding's first piece of evidence.

**Step 2 — determine the query shape.** The page returns two columns. A union-based test must match that count:

```text
1' UNION SELECT first_name, password FROM users -- 
```

**Expected:** the page's result table contains a name and a hash-like string where the surname used to be.

**Step 3 — write the finding.** Not "SQL injection in `id`". Instead: *the `id` parameter is interpolated into a
query, so an unauthenticated visitor can read any table the application's database user can access, including
credential hashes; demonstrated by returning `users.password` in the response.*

**Step 4 — fix and prove it.** In a local copy, replace the interpolation:

```python
# app.py — the safe version of the same feature
import sqlite3

def get_user(db_path: str, user_id: str):
    """Return one user by id. user_id is data, never syntax."""
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT first_name, last_name FROM users WHERE user_id = ?", (user_id,))
        return cur.fetchone()
```

**Step 5 — verify both directions.** A fix is only proven when the attack fails *and* the feature works:

```python
# tests/test_injection.py
import sqlite3
from app import get_user

def _seed():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (user_id TEXT, first_name TEXT, last_name TEXT)")
    conn.execute("INSERT INTO users VALUES ('1','Amina','Riaz')")
    return conn

def test_legitimate_lookup_still_works(tmp_path):
    db = str(tmp_path / "t.db")
    conn = sqlite3.connect(db); conn.execute("CREATE TABLE users (user_id TEXT, first_name TEXT, last_name TEXT)")
    conn.execute("INSERT INTO users VALUES ('1','Amina','Riaz')"); conn.commit(); conn.close()
    assert get_user(db, "1") == ("Amina", "Riaz")

def test_injection_payload_returns_nothing(tmp_path):
    db = str(tmp_path / "t.db")
    conn = sqlite3.connect(db); conn.execute("CREATE TABLE users (user_id TEXT, first_name TEXT, last_name TEXT)")
    conn.execute("INSERT INTO users VALUES ('1','Amina','Riaz')"); conn.commit(); conn.close()
    assert get_user(db, "1' OR '1'='1") is None
```

The second test is the regression guard. Without it, the next developer's refactor can quietly reintroduce
concatenation and no test will notice.

---

## Defender's view

| Signal | Where to look | Interpretation |
| --- | --- | --- |
| Database error text in a response | Application logs, response body | Error-based injection attempt, or a genuine bug — either way, verbose errors must go |
| Repeated `500`s from one parameter | WAF, reverse proxy | Fuzzing |
| Quotes, `UNION`, comment markers in query strings | Access logs, WAF | Injection probes; usually automated, but confirm with timing and source |
| `OR 1=1` in a POST body | Body logging (careful with PII) | Authentication bypass attempt |
| Script tags in a stored field | Application audit log, database triggers | Stored XSS seeding |
| CSP violation reports | `report-uri`/`report-to` endpoint | Either an attack or a broken deployment; both are actionable |
| Same account, many parameter variants | App logs with session ID | Manual testing, not a scanner |

Defensive posture, in order of value: parameterised queries everywhere (with an allowlist for identifiers);
context-aware output encoding on by default in the template engine; a nonce-based CSP with `object-src 'none'`;
`HttpOnly` session cookies so an XSS cannot immediately become account takeover; and an allowlist-based HTML
sanitiser wherever rich text is unavoidable.

---

## Common mistakes

1. **Escaping on input.** It corrupts data (`O'Brien` becomes `O&#39;Brien` in the database), breaks exports, and
   does not protect non-HTML consumers. Encode on output.
2. **Believing prepared statements cover `ORDER BY`.** They cannot bind identifiers. Use an allowlist and say so
   in the report.
3. **Testing XSS with `<script>alert(1)</script>` only.** It fails in attribute and JS contexts, and many apps
   block that one string. Test each context with a payload appropriate to it.
4. **Calling a WAF a fix.** A WAF changes the cost of exploitation; it does not change the code. Report it as
   compensating, never as remediation.
5. **Forgetting the second half of verification.** A patch with no regression test is a patch that will regress.
6. **Reporting reflected XSS as High by default.** Severity depends on what the session can do and whether
   `HttpOnly` limits theft. State the reasoning; do not copy a CVSS number.

---

## Practice

1. [LAB-302-01 · SQL Injection and Its Fix](lab-01-sql-injection.md) — four techniques, then a parameterised
   rewrite with tests.
2. [LAB-302-02 · Reflected and Stored XSS](lab-02-xss.md) — three contexts, then encoding and CSP that actually
   block the payload.

**Stretch task.** Take the union-based query you built and rewrite it so the same information is returned through
an allowlisted sort parameter (`ORDER BY`), then write the test that proves injection through that parameter
fails. This is the case most reviews miss.

## Knowledge check

1. Why does parameter binding prevent SQL injection, in terms of when the query is parsed?
2. A developer writes `ORDER BY ?` and finds it "doesn't work". What is the correct fix, and why can it not be a
   placeholder?
3. Name the four SQL injection techniques and the precondition each depends on.
4. Why is HTML entity encoding useless inside a `<script>` block?
5. An application blocks `<script>` and `onerror`. Give two reasons this is not a fix.
6. Where does DOM-based XSS execute, and why can no server-side filter see it?
7. A CSP is present with `script-src 'self' 'unsafe-inline'`. What is its practical value against reflected XSS?
8. Your fix binds the parameter, and the attack now returns an empty page. What second test is still required?

## Summary

- Injection is `interpreter(fixed_text + user_data)`; the fix is to keep data out of the syntax.
- Parameter binding works because the query is parsed before the data is supplied.
- SQL injection techniques differ in precondition and output, not in root cause.
- XSS is injection into the browser; the correct encoding depends on the context of use.
- CSP limits impact; it never replaces output encoding, and `unsafe-inline` makes it decorative.
- Remediation is proven by an attack that now fails **and** a feature that still works.

## References

1. OWASP Top 10:2025 — A05 Injection. <https://owasp.org/Top10/2025/> Accessed 2026-10-29.
2. OWASP SQL Injection Prevention Cheat Sheet. Accessed 2026-10-29.
3. OWASP Cross Site Scripting Prevention Cheat Sheet. Accessed 2026-10-29.
4. OWASP WSTG v4.2 — WSTG-INPV-01, WSTG-INPV-02, WSTG-INPV-05.
5. OWASP ASVS 5.0 — V1 Encoding and Sanitization. <https://asvs.owasp.org/> Accessed 2026-10-29.
6. MDN — Content-Security-Policy. Accessed 2026-10-29.
