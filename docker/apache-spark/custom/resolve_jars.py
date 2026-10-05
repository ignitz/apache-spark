"""Copy Ivy-resolved JARs that Spark does not already ship.

Ivy names files `<group>_<artifact>-<version>.jar`; Spark ships `<artifact>-<version>.jar`.
An artifact already present in Spark is skipped (Spark's version wins), so the image never
carries two versions of the same library (Jackson, Netty, Guava, ...).

Usage: resolve_jars.py <ivy_jars_dir> <spark_jars_dir> <out_dir>
Writes a manifest of what was added / skipped to <out_dir>.txt.
"""

import re
import shutil
import sys
from pathlib import Path

# Artifacts whose classes clash with differently-named Spark jars:
#   commons-logging -> Spark routes JCL through jcl-over-slf4j
#   shims           -> RoaringBitmap 0.9.x helper, already inside Spark's RoaringBitmap 1.x
DENY = {"commons-logging", "shims"}

VERSIONED = re.compile(r"^(?P<artifact>.+?)-(?P<version>\d[^-]*(?:-[A-Za-z0-9.]+)*)\.jar$")


def artifact_of(filename: str) -> str:
    m = VERSIONED.match(filename)
    return m.group("artifact") if m else filename.removesuffix(".jar")


def main(ivy_dir: str, spark_dir: str, out_dir: str) -> None:
    spark_artifacts = {artifact_of(p.name): p.name for p in Path(spark_dir).glob("*.jar")}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    added, skipped = [], []
    for jar in sorted(Path(ivy_dir).glob("*.jar")):
        _, _, name = jar.name.partition("_")
        artifact = artifact_of(name)
        if artifact in spark_artifacts:
            skipped.append(f"{jar.name}  (spark ships {spark_artifacts[artifact]})")
            continue
        if artifact in DENY:
            skipped.append(f"{jar.name}  (deny-listed: clashes with Spark classes)")
            continue
        shutil.copy2(jar, out / name)
        added.append(name)

    report = ["# added"] + added + ["", "# skipped"] + skipped
    Path(f"{out_dir.rstrip('/')}.txt").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main(*sys.argv[1:4])
