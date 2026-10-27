# NORMALIZER_REVIEW — compact evidence for the 100-pair gate

Full detail (both patches + both canonical forms per pair): [NORMALIZER_VALIDATION.md](NORMALIZER_VALIDATION.md). Raw patch files: `out/validation_pairs/`.

Read this as: does each **different** verdict have a real cause, and does each **identical** verdict hide a real difference?


## Pairs judged DIFFERENT (check: is the difference real?)

| pair | instance | cause | first differing line A | first differing line B |
|---|---|---|---|---|
| linkml__linkml-runtime-132__1 | linkml__linkml-runtime-132 | file set | `SOLUTION_SUMMARY.md` | `.openhands/TASKS.md` |
| biolink__biolink-model-toolkit-51__2 | biolink__biolink-model-toolkit-51 | file set | `-    return stringcase.sentencecase(s).lower()` | `-    Convert CamelCase to sentence case.` |
| tuw-geo__pygeogrids-66__3 | tuw-geo__pygeogrids-66 | file set | `+1. ✅ Reading and understanding the problem` | `+1. ✅ Fix the max_dist parameter bug in find_nearest_gpi` |
| collective__icalendar-391__4 | collective__icalendar-391 | file set | `comprehensive_test.py` | `src/icalendar/prop.py` |
| cartodb__cartoframes-379__5 | cartodb__cartoframes-379 | file set | `.openhands/TASKS.md` | `cartoframes/layer.py` |
| tobymao__sqlglot-3682__6 | tobymao__sqlglot-3682 | file set | `debug_issue.py` | `debug_array_logic.py` |
| rockefellerarchivecenter__dacsspace-39__7 | rockefellerarchivecenter__dacsspace-39 | file set | `-    def run(self, published_only, invalid_only):` | `-            result = validator.validate(obj)` |
| apptuitai__apptuit-py-10__8 | apptuitai__apptuit-py-10 | file set | `.openhands/TASKS.md` | `apptuit/apptuit_client.py` |
| ncclient__ncclient-452__9 | ncclient__ncclient-452 | file set | `ncclient/operations/retrieve.py` | `comprehensive_test.py` |
| geopandas__geopandas-3240__10 | geopandas__geopandas-3240 | file set | `+` | `+"""` |
| tannerlinsley__react-query-3343__1 | tannerlinsley__react-query-3343 | content | `+    let settled = false` | `+    let onSettledCalled = false` |
| hetznercloud__hcloud-go-42__2 | hetznercloud__hcloud-go-42 | content | `+// create an enable_backup server action.` | `+// create a enable_backup server action.` |
| more-itertools__more-itertools-892__3 | more-itertools__more-itertools-892 | content | `+def sort_together(` | `+def sort_together(iterables, key_list=(0,), key=None, reverse=False, ` |
| styleguidist__react-styleguidist-1690__4 | styleguidist__react-styleguidist-1690 | file set | `src/scripts/make-webpack-config.ts` | `src/loaders/utils/highlightCode.ts` |
| roave__betterreflection-601__5 | roave__betterreflection-601 | file set | `src/Reflection/Adapter/ReflectionClass.php` | `src/Reflection/ReflectionClass.php` |
| remarkablemark__html-react-parser-1260__6 | remarkablemark__html-react-parser-1260 | file set | `src/dom-to-react.ts` | `README.md` |
| dtolnay__cxx-190__7 | dtolnay__cxx-190 | file set | `README.md` | `gen/build/src/lib.rs` |
| jiangzhe__xngin-20__8 | jiangzhe__xngin-20 | content | `+/// OpKind enumerates the logical operator kinds used throughout the ` | `+/// OpKind represents the kind of a logical operator.` |
| lo1tuma__eslint-plugin-mocha-316__9 | lo1tuma__eslint-plugin-mocha-316 | content | `-}` | `+function isFunctionExpression(node) {` |
| zauberzeug__nicegui-625__10 | zauberzeug__nicegui-625 | content | `+import time` | `+import webbrowser` |
| googleapis__java-storage-1389__1 | googleapis__java-storage-1389 | content | `+       */` | `+       *` |
| getmoto__moto-8199__2 | getmoto__moto-8199 | content | `` | `+                    return_values_on_condition_check_failure = item.g` |
| bvanelli__actualpy-74__3 | bvanelli__actualpy-74 | file set | `-from actual.exceptions import ActualError, InvalidZipFile, UnknownFil` | `+from actual.api.bank_sync import BankSyncErrorDTO` |
| skeletonlabs__floating-ui-svelte-79__4 | skeletonlabs__floating-ui-svelte-79 | file set | `` | `<end>` |
| swc-project__swc-7437__5 | swc-project__swc-7437 | content | `-            if !contains_rest(for_stmt) {` | `+            let mut visited_body = false;` |
| smithy-lang__smithy-2247__6 | smithy-lang__smithy-2247 | file set | `-import java.util.logging.Logger;` | `+                // Emit a warning event for duplicate shape definitio` |
| open-feature__java-sdk-1228__7 | open-feature__java-sdk-1228 | content | `+     * @param details   TrackingEventDetails containing structured ev` | `+     * @param details   TrackingEventDetails containing event details` |
| pallets__jinja-1613__8 | pallets__jinja-1613 | content | `+        @wraps(async_func)` | `+        # Use wraps(async_func) instead of wraps(normal_func) to pres` |
| cta-observatory__ctapipe-2397__9 | cta-observatory__ctapipe-2397 | content | `+        pix_indices: Pixel index or array of pixel indices.` | `+        pix_indices: Pixel index or array of pixel indices. Returns n` |
| apollographql__apollo-tooling-2335__10 | apollographql__apollo-tooling-2335 | content | `+  let anyTypeModified = false;` | `-  GraphQLInputFieldConfigMap` |
| pallets__click-1679__1 | pallets__click-1679 | content | `+        self._main_shell_completion(extra, prog_name, complete_var)` | `+        self._main_shell_completion(prog_name, complete_var, extra)` |
| tikv__pd-7087__2 | tikv__pd-7087 | file set | `-	rd *render.Render` | `+` |
| open-feature__java-sdk-34__3 | open-feature__java-sdk-34 | file set | `+    ProviderEvaluation<Double> getDoubleEvaluation(String key, Double` | `+    default ProviderEvaluation<Double> getDoubleEvaluation(String key` |
| iterative__cml-1100__4 | iterative__cml-1100 | content | `+    const formattedKey = /[\s.]\|^[0-9]/.test(key) ? `"${key}"` : key;` | `+    const needsQuoting = /[^a-zA-Z0-9_]/.test(key);` |
| remarkablemark__html-react-parser-780__5 | remarkablemark__html-react-parser-780 | content | `+var domhandler = require('domhandler');` | `-HTMLReactParser.Element = require('domhandler').Element;` |
| supabase__gotrue-1368__6 | supabase__gotrue-1368 | content | `+// MaxPasswordLength is the maximum length of a password in bytes.` | `+` |
| google__jax-22541__7 | google__jax-22541 | file set | `+  if isinstance(shape, int) or isinstance(shape, np.integer):` | `+  # Handle the case where shape is a single integer (treated as 1D sh` |
| fatiando__verde-29__8 | fatiando__verde-29 | content | `+                 adjust='spacing', center_coordinates=False):` | `+                  adjust='spacing', center_coordinates=False):` |
| joshuakgoldberg__create-typescript-app-1822__9 | joshuakgoldberg__create-typescript-app-1822 | file set | `src/next/base.ts` | `src/shared/options/createOptionDefaults/getUsageFromReadme.ts` |
| paustint__soql-parser-js-82__10 | paustint__soql-parser-js-82 | content | `-  let currUnAliasedAggExp = -1;` | `+export function getFlattenedFields(` |
| projectmesa_mesa_pr2512__1 | projectmesa_mesa_pr2512 | content | `+import contextlib` | `+        self._update_occupancy()` |
| jackdewinter_pymarkdown_pr384__2 | jackdewinter_pymarkdown_pr384 | file set | `pymarkdown/list_block_processor.py` | `pymarkdown/container_block_processor.py` |
| chimpler_pyhocon_pr85__3 | chimpler_pyhocon_pr85 | file set | `pyhocon/config_parser.py` | `pyhocon/__init__.py` |
| erikbern_synchronicity_pr11__4 | erikbern_synchronicity_pr11 | content | `+If you want to explicitly control the execution mode, rather than rel` | `+You can also override the automatic detection of the context and forc` |
| xgcm_xrft_pr126__5 | xgcm_xrft_pr126 | content | `-    dk = [l[1] - l[0] for l in wavenm]` | `-    k_coords = {key: val for (key, val) in zip(k_names, wavenm)}` |
| biopragmatics_bioregistry_pr675__6 | biopragmatics_bioregistry_pr675 | file set | `+#: Prefixes in Prefix Commons that are "providers" for another, canon` | `+    # providers of PDB` |
| dbt-labs_dbt-adapters_pr126__7 | dbt-labs_dbt-adapters_pr126 | content | `+` | `+    TYPE_CHECKING,` |
| mongodb_mongo-python-driver_pr1731__8 | mongodb_mongo-python-driver_pr1731 | content | `-        self._exhaust = False` | `+            # The exhaust support check (is_mongos) requires network ` |
| peterbe_hashin_pr95__9 | peterbe_hashin_pr95 | content | `+def _hash_directive(line):` | `+def _canonicalize_requirement_block(block):` |
| fastavro_fastavro_pr381__10 | fastavro_fastavro_pr381 | content | `+try:` | `+cpdef lz4_read_block(fo):` |

Cause split: 26 content differences, 24 file-set differences (of 50).


## Pairs judged IDENTICAL (sample of 12 — check: is this really the same change?)


**duke-gcb__dukedsclient-317__1** · `duke-gcb__dukedsclient-317` · 2 changed lines · files: `ddsc/config.py`

```diff
ddsc/config.py
+        if new_values is None:
+            new_values = {}
```


**gouline__dbt-metabase-224__2** · `gouline__dbt-metabase-224` · 64 changed lines · files: `dbtmetabase/_exposures.py|issue.md`

```diff
dbtmetabase/_exposures.py
-                )["models"]
+                )["depends"]
-                    )["models"]
+                    )["depends"]

issue.md
+### Exposures command fails. dbtmetabase/_exposures.py; Function: __extract_card_exposures(); dbt-metabase: 1.0.1
+When I run `dbt-metabase exposures` I get the following error:
+
+```bash
+Traceback (most recent call last):
+  File "/pypoetry/virtualenvs/dbt-yDNzCqHh-py3.10/bin/dbt-metabase", line 8, in <module>
+    sys.exit(cli())
+  File "/pypoetry/virtualenvs/dbt-yDNzCqHh-py3.10/lib/python3.10/site-packages/click/core.py", line 
…
```


**keis__base58-46__3** · `keis__base58-46` · 42 changed lines · files: `base58.egg-info/PKG-INFO|base58.egg-info/SOURCES.txt|base58.egg-info/dependency_links.txt|base58.egg-info/entry_points.txt|base58.egg-info/top_level.txt|base58.py`

```diff
base58.egg-info/PKG-INFO
+Metadata-Version: 2.2
+Name: base58
+Version: 1.0.3
+Summary: Base58 and Base58Check implementation
+Home-page: https://github.com/keis/base58
+Author: David Keijser
+Author-email: keijser@gmail.com
+License: MIT
+Classifier: Development Status :: 5 - Production/Stable
+Classifier: Intended Audience :: Developers
+Classifier: Natural Language :: English
+Classifier: License :: OSI Approved :: MIT License
+Classifier: Programming Language :: Python
+Classifier: Programming Language :: Python :: 3
+Requires-Python: >=3.5
+License-File: COPYING
+Dynamic: author
+Dynamic:
…
```


**canonical__operator-914__4** · `canonical__operator-914` · 1 changed lines · files: `MANIFEST.in`

```diff
MANIFEST.in
+include requirements.txt
```


**simonw__files-to-prompt-30__5** · `simonw__files-to-prompt-30` · 5 changed lines · files: `files_to_prompt/cli.py`

```diff
files_to_prompt/cli.py
+                dirs[:] = [
+                    d
+                    for d in dirs
+                    if not any(fnmatch(d, pattern) for pattern in ignore_patterns)
+                ]
```


**googlemaps__google-maps-services-python-374__6** · `googlemaps__google-maps-services-python-374` · 2 changed lines · files: `googlemaps/maps.py`

```diff
googlemaps/maps.py
-            if len(label) != 1 or not label.isupper() or not label.isalnum():
+            if len(label) != 1 or not label.isalnum() or (label.isalpha() and not label.isupper()):
```


**esmvalgroup__esmvalcore-2485__7** · `esmvalgroup__esmvalcore-2485` · 2 changed lines · files: `esmvalcore/config/extra_facets/access-mappings.yml`

```diff
esmvalcore/config/extra_facets/access-mappings.yml
-ACCESS_ESM:
+ACCESS-ESM1-5:
```


**snowflakedb__snowflake-connector-python-1094__8** · `snowflakedb__snowflake-connector-python-1094` · 4 changed lines · files: `src/snowflake/connector/connection.py`

```diff
src/snowflake/connector/connection.py
-        self.connect(**kwargs)
-        self._telemetry = TelemetryClient(self._rest)
+        self.connect(**kwargs)
+        self._telemetry = TelemetryClient(self._rest)
```


**somm15__pyvicare-313__9** · `somm15__pyvicare-313` · 79 changed lines · files: `PyViCare/PyViCareHeatingDevice.py|issue.md`

```diff
PyViCare/PyViCareHeatingDevice.py
+    @handleNotSupported
+    def getProgramMinTemperature(self, program: str):
+        if program in ['standby']:
+            return None
+
+        return self.service.getProperty(f"heating.circuits.{self.circuit}.operating.programs.{program}")[
+            "commands"]["setTemperature"]["params"]["targetTemperature"]["constraints"]["min"]
+
+    @handleNotSupported
+    def getProgramMaxTemperature(self, program: str):
+        if program in ['standby']:
+            return None
+
+        return self.service.getProperty(f"heating.circuits.{self.circuit}.
…
```


**terrapower__armi-256__10** · `terrapower__armi-256` · 300 changed lines · files: `armi/bookkeeping/visualization/utils.py`

```diff
armi/bookkeeping/visualization/utils.py
-# Copyright 2020 TerraPower, LLC
-#
-# Licensed under the Apache License, Version 2.0 (the "License");
-# you may not use this file except in compliance with the License.
-# You may obtain a copy of the License at
-#
-#     http://www.apache.org/licenses/LICENSE-2.0
-#
-# Unless required by applicable law or agreed to in writing, software
-# distributed under the License is distributed on an "AS IS" BASIS,
-# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-# See the License for the specific language governing permissions and
-#
…
```


**typescript-eslint__tslint-to-eslint-config-536__1** · `typescript-eslint__tslint-to-eslint-config-536` · 6 changed lines · files: `src/comments/convertComments.ts|src/reporting/reportCommentResults.ts`

```diff
src/comments/convertComments.ts
-    errors: [new Error("--comment requires file path globs to be passed.")],
+    errors: [new Error("--comments requires file path globs to be passed.")],

src/reporting/reportCommentResults.ts
-        } converting TSLint comment directives in --comment files`;
+        } converting TSLint comment directives in --comments files`;
-                `${EOL}♻ Consider using --comment to replace TSLint comment directives in your source files. ♻${EOL}`,
+                `${EOL}♻ Consider using --comments to replace TSLint comment directives in your source files. ♻$
…
```


**joshuakgoldberg__create-typescript-app-1735__2** · `joshuakgoldberg__create-typescript-app-1735` · 6 changed lines · files: `src/steps/writing/creation/dotGitHub/createMultiWorkflowFile.ts|src/steps/writing/creation/dotGitHub/createWorkflows.ts`

```diff
src/steps/writing/creation/dotGitHub/createMultiWorkflowFile.ts
-export type MultiWorkflowJobStep = { run: string } | { uses: string };
+export type MultiWorkflowJobStep =
+	| { if?: string; run: string }
+	| { if?: string; uses: string };

src/steps/writing/creation/dotGitHub/createWorkflows.ts
-									{ uses: "codecov/codecov-action@v3" },
+									{ if: "always()", uses: "codecov/codecov-action@v3" },
```
