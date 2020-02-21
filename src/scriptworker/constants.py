#!/usr/bin/env python
"""scriptworker constants.

Attributes:
    DEFAULT_CONFIG (immutabledict): the default config for scriptworker.  Running configs
        are validated against this.
    STATUSES (dict): maps taskcluster status (string) to exit code (int).

"""
import os
from typing import Any, Dict

from immutabledict import immutabledict

STATUSES = {
    "success": 0,
    "failure": 1,
    "worker-shutdown": 2,
    "malformed-payload": 3,
    "resource-unavailable": 4,
    "internal-error": 5,
    "superseded": 6,
    "intermittent-task": 7,
}

# DEFAULT_CONFIG {{{1
# When making changes to DEFAULT_CONFIG that may be of interest to scriptworker
# instance maintainers, also make changes to ``scriptworker.yaml.tmpl``.
#
# Often DEFAULT_CONFIG changes will require test changes as well.
#
# When adding new complex config, make sure all `list`s are `tuple`s, and all
# `dict`s are `immutabledict`s!  (This should get caught by config tests.)
DEFAULT_CONFIG = immutabledict(
    {
        "taskcluster_root_url": os.environ.get("TASKCLUSTER_ROOT_URL", "https://firefox-ci-tc.services.mozilla.com/"),
        # Worker identification
        "provisioner_id": "test-dummy-provisioner",
        "worker_group": "test-dummy-workers",
        "worker_type": "dummy-worker-myname",
        "worker_id": os.environ.get("SCRIPTWORKER_WORKER_ID", "dummy-worker-myname1"),
        "credentials": immutabledict({"clientId": "...", "accessToken": "...", "certificate": "..."}),
        # Worker log settings
        "log_datefmt": "%Y-%m-%dT%H:%M:%S",
        "log_fmt": "%(asctime)s %(levelname)8s - %(message)s",
        "watch_log_file": False,
        # intervals are expressed in seconds
        "task_max_timeout": 60 * 20,
        "reclaim_interval": 300,
        "poll_interval": 10,
        "sign_key_timeout": 60 * 2,
        "reversed_statuses": immutabledict({-11: STATUSES["intermittent-task"], -15: STATUSES["intermittent-task"]}),
        # Report this status on max_timeout. `intermittent-task` will rerun the
        # task automatically. `internal-error` or other will require manual
        # intervention.
        "task_max_timeout_status": STATUSES["intermittent-task"],
        "invalid_reclaim_status": STATUSES["intermittent-task"],
        "task_script": ("bash", "-c", "echo foo && sleep 19 && exit 1"),
        "verbose": True,
        # Task settings
        "work_dir": "...",
        "log_dir": "...",
        "artifact_dir": "...",
        "task_log_dir": "...",  # set this to ARTIFACT_DIR/public/logs
        "artifact_upload_timeout": 60 * 20,
        "aiohttp_max_connections": 15,
        # chain of trust settings
        "sign_chain_of_trust": True,
        "verify_chain_of_trust": False,  # TODO True
        "verify_cot_signature": False,
        "cot_job_type": "unknown",  # e.g., signing
        "cot_product": "firefox",
        "cot_version": 3,
        "min_cot_version": 2,
        "max_chain_length": 20,
        # Calls to Github API are limited to 60 an hour. Using an API token allows to raise the limit to
        # 5000 per hour. https://developer.github.com/v3/#rate-limiting
        "github_oauth_token": "",
        # ed25519 settings
        "ed25519_private_key_path": "...",
        "ed25519_public_keys": immutabledict(
            {
                # the key beginning in J+PAK... is the longstanding docker-worker CoT key, to be phased out
                # the key beginning in tk/Sj... is a new key added to differentiate GCP workers
                "docker-worker": tuple(["J+PAKmq3jkS2uCpBk5WU2ycrnTFPwZujJT4OHAxm38I=", "tk/SjxY3mREARba6ODw7qReUoVWj0RgEIxBURkwcM4I="]),
                "generic-worker": tuple(["6UPrVTyw0EPQV7bCEMXo+5jNR4clbK55JWG74bBJHZQ="]),
                "scriptworker": tuple(["DaEKQ79ZC/X+7O8zwm8iyhwTlgyjRSi/TDd63fh2JG0="]),
            }
        ),
        "project_configuration_url": "https://hg.mozilla.org/ci/ci-configuration/raw-file/default/projects.yml",
        "pushlog_url": "{repo}/json-pushes?changeset={revision}&tipsonly=1&version=2&full=1",
        "chain_of_trust_hash_algorithm": "sha256",
        "cot_schema_path": os.path.join(os.path.dirname(__file__), "data", "cot_v1_schema.json"),
        # for download url validation.  The regexes need to define a 'filepath'.
        "valid_artifact_rules": (
            immutabledict(
                {
                    "schemes": ("https",),
                    "netlocs": ("queue.taskcluster.net",),
                    "path_regexes": (r"^/v1/task/(?P<taskId>[^/]+)(/runs/\\d+)?/artifacts/(?P<filepath>.*)$",),
                }
            ),
            immutabledict(
                {
                    "schemes": ("https",),
                    "netlocs": ("firefox-ci-tc.services.mozilla.com", "stage.taskcluster.nonprod.cloudops.mozgcp.net"),
                    "path_regexes": (r"^/api/queue/v1/task/(?P<taskId>[^/]+)(/runs/\\d+)?/artifacts/(?P<filepath>.*)$",),
                }
            ),
        ),
        "scriptworker_provisioners": ("scriptworker-prov-v1", "scriptworker-k8s"),
        # valid hash algorithms for chain of trust artifacts
        "valid_hash_algorithms": ("sha256", "sha512"),
        # decision task cot
        "valid_decision_worker_pools": immutabledict(
            {
                "by-cot-product": immutabledict(
                    {
                        "firefox": (
                            "aws-provisioner-v1/gecko-1-decision",
                            "aws-provisioner-v1/gecko-2-decision",
                            "aws-provisioner-v1/gecko-3-decision",
                            "gecko-1/decision",
                            "gecko-2/decision",
                            "gecko-3/decision",
                        ),
                        "thunderbird": (
                            "aws-provisioner-v1/gecko-1-decision",
                            "aws-provisioner-v1/gecko-2-decision",
                            "aws-provisioner-v1/gecko-3-decision",
                            "comm-1/decision",
                            "comm-2/decision",
                            "comm-3/decision",
                        ),
                        "mobile": (
                            # gecko-focus was for mozilla-mobile releases (bug 1455290) for more details.
                            # TODO: Remove it once not used anymore
                            "aws-provisioner-v1/gecko-focus",
                            "aws-provisioner-v1/mobile-1-decision",
                            # We haven't had the need for mobile-2-decision yet
                            # https://bugzilla.mozilla.org/show_bug.cgi?id=1512631#c6
                            "aws-provisioner-v1/mobile-3-decision",
                            "mobile-1/decision",
                            "mobile-3/decision",
                        ),
                        "mpd001": ("aws-provisioner-v1/mpd001-1-decision", "aws-provisioner-v1/mpd001-3-decision", "mpd001-1/decision", "mpd001-3/decision"),
                        "application-services": (
                            "aws-provisioner-v1/app-services-1-decision",
                            "aws-provisioner-v1/app-services-3-decision",
                            "app-services-1/decision",
                            "app-services-3/decision",
                        ),
                        "xpi": ("xpi-1/decision", "xpi-3/decision"),
                        # TODO: Add adhoc-3 whenever we're ready to go to prod
                        "adhoc": ("adhoc-1/decision",),
                    }
                )
            }
        ),
        # docker-image cot
        "valid_docker_image_worker_pools": immutabledict(
            {
                "by-cot-product": immutabledict(
                    {
                        "firefox": (
                            "aws-provisioner-v1/gecko-1-images",
                            "aws-provisioner-v1/gecko-2-images",
                            "aws-provisioner-v1/gecko-3-images",
                            "gecko-1/images",
                            "gecko-2/images",
                            "gecko-3/images",
                        ),
                        "thunderbird": (
                            "aws-provisioner-v1/gecko-1-images",
                            "aws-provisioner-v1/gecko-2-images",
                            "aws-provisioner-v1/gecko-3-images",
                            "comm-1/images",
                            "comm-2/images",
                            "comm-3/images",
                        ),
                        "mobile": (
                            "aws-provisioner-v1/mobile-1-images",  # there is no mobile level 2.
                            "aws-provisioner-v1/mobile-3-images",
                            "mobile-1/images",
                            "mobile-3/images",
                        ),
                        "mpd001": ("aws-provisioner-v1/mpd001-1-images", "aws-provisioner-v1/mpd001-3-images", "mpd001-1/images", "mpd001-3/images"),
                        "application-services": (
                            "aws-provisioner-v1/app-services-1-images",
                            "aws-provisioner-v1/app-services-3-images",
                            "app-services-1/images",
                            "app-services-3/images",
                        ),
                        "xpi": ("xpi-1/images", "xpi-3/images"),
                        # TODO: Add adhoc-3 whenever we're ready to go to prod
                        "adhoc": ("adhoc-1/images",),
                    }
                )
            }
        ),
        # for trace_back_to_*_tree.  These repos have access to restricted scopes;
        # all other repos are relegated to CI scopes.
        "trusted_vcs_rules": {
            "by-cot-product": immutabledict(
                {
                    "firefox": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("hg.mozilla.org",),
                                "path_regexes": (
                                    r"^(?P<path>/mozilla-(central|unified))(/|$)",
                                    r"^(?P<path>/integration/(autoland|fx-team|mozilla-inbound))(/|$)",
                                    r"^(?P<path>/releases/mozilla-(beta|release|esr\d+))(/|$)",
                                    r"^(?P<path>/projects/(birch|jamun|maple|oak))(/|$)",
                                ),
                            }
                        ),
                    ),
                    # XXX We should also check the mozilla-central tree that is being used.
                    "thunderbird": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("hg.mozilla.org",),
                                "path_regexes": (r"^(?P<path>/comm-central)(/|$)", r"^(?P<path>/releases/comm-(beta|esr\d+))(/|$)"),
                            }
                        ),
                    ),
                    "mobile": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("github.com",),
                                "path_regexes": tuple(
                                    [
                                        r"^(?P<path>/mozilla-mobile/"
                                        "(?:"
                                        "android-components"
                                        "|fenix"
                                        "|fennec-profile-manager"
                                        "|firefox-tv"
                                        "|focus-android"
                                        "|reference-browser"
                                        "))"
                                        "(/|.git|$)"
                                    ]
                                ),
                            }
                        ),
                    ),
                    "mpd001": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("github.com",),
                                "path_regexes": tuple([r"^(?P<path>/mozilla-services/(?:guardian-vpn))(/|.git|$)"]),
                                "require_secret": True,
                            }
                        ),
                    ),
                    "application-services": (
                        immutabledict(
                            {"schemes": ("https", "ssh"), "netlocs": ("github.com",), "path_regexes": (r"^(?P<path>/mozilla/application-services)(/|.git|$)",)}
                        ),
                    ),
                    "xpi": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("github.com",),
                                "path_regexes": tuple([r"^(?P<path>/mozilla-extensions/xpi-manifest)(/|.git|$)"]),
                            }
                        ),
                    ),
                    "adhoc": (
                        immutabledict(
                            {
                                "schemes": ("https", "ssh"),
                                "netlocs": ("github.com",),
                                # TODO: Change repo to its final name
                                "path_regexes": tuple([r"^(?P<path>/mozilla-releng/mvp-adhoc)(/|.git|$)"]),
                            }
                        ),
                    ),
                }
            )
        },
        "valid_tasks_for": {
            "by-cot-product": immutabledict(
                {
                    "firefox": ("hg-push", "cron", "action"),
                    "thunderbird": ("hg-push", "cron", "action"),
                    "mobile": (
                        "action",
                        "cron",
                        # On staging releases, level 1 docker images may be built in the pull-request graph
                        "github-pull-request",
                        # Similarly, docker images can be built on regular push. This is usually the case
                        # for level 3 images
                        "github-push",
                        "github-release",
                    ),
                    "mpd001": ("cron", "github-pull-request", "github-push", "github-release"),
                    "application-services": (
                        # On staging releases, level 1 docker images may be built in the pull-request graph
                        "github-pull-request",
                        # Similarly, docker images can be built on regular push. This is usually the case
                        # for level 3 images
                        "github-release",
                    ),
                    "xpi": ("action", "cron", "github-pull-request", "github-push", "github-release"),
                    "adhoc": ("action", "github-pull-request", "github-push",),
                }
            )
        },
        "official_github_repos_owner": {
            "by-cot-product": immutabledict(
                {
                    "firefox": "",
                    "thunderbird": "",
                    "mobile": "mozilla-mobile",
                    "mpd001": "mozilla-services",
                    "application-services": "mozilla",
                    "xpi": "mozilla-extensions",
                    "adhoc": "mozilla-releng",
                }
            )
        },
        # Map scopes to restricted-level
        "cot_restricted_scopes": {
            "by-cot-product": immutabledict(
                {
                    "firefox": immutabledict(
                        {
                            "project:releng:addons.mozilla.org:server:production": "all-release-branches",
                            "project:releng:balrog:server:nightly": "all-nightly-branches",
                            "project:releng:balrog:server:beta": "beta",
                            "project:releng:balrog:server:release": "release",
                            "project:releng:balrog:server:esr": "esr",
                            "project:releng:beetmover:bucket:nightly": "all-nightly-branches",
                            "project:releng:beetmover:bucket:release": "all-release-branches",
                            "project:releng:bouncer:server:production": "all-production-branches",
                            # Fennec rides the 68 train. This means, Fennec Nightly will first be shipped off
                            # mozilla-central then mozilla-esr68. Fennec Beta and Release will move to
                            # mozilla-esr68 too.
                            "project:releng:googleplay:aurora": "esr68",
                            "project:releng:googleplay:beta": "esr68",
                            "project:releng:googleplay:release": "esr68",
                            "project:releng:signing:cert:nightly-signing": "all-nightly-branches",
                            "project:releng:signing:cert:release-signing": "all-release-branches",
                            "project:releng:snapcraft:firefox:beta": "beta-or-release",  # Needed on release for RCs
                            "project:releng:snapcraft:firefox:candidate": "release",
                            "project:releng:snapcraft:firefox:esr": "esr",
                            "project:releng:ship-it:production": "all-production-branches",
                            "project:releng:treescript:action:push": "all-production-branches",
                        }
                    ),
                    "thunderbird": immutabledict(
                        {
                            "project:comm:thunderbird:releng:balrog:server:nightly": "all-nightly-branches",
                            "project:comm:thunderbird:releng:balrog:server:beta": "beta",
                            "project:comm:thunderbird:releng:balrog:server:esr": "esr",
                            "project:comm:thunderbird:releng:beetmover:bucket:nightly": "all-nightly-branches",
                            "project:comm:thunderbird:releng:beetmover:bucket:release": "all-release-branches",
                            "project:comm:thunderbird:releng:bouncer:server:production": "all-release-branches",
                            "project:comm:thunderbird:releng:signing:cert:nightly-signing": "all-nightly-branches",
                            "project:comm:thunderbird:releng:signing:cert:release-signing": "all-release-branches",
                        }
                    ),
                    "mobile": immutabledict(
                        {
                            "project:mobile:android-components:releng:beetmover:bucket:maven-production": "android-components-repo",
                            "project:mobile:android-components:releng:beetmover:bucket:maven-snapshot-production": "android-components-repo",
                            "project:mobile:fenix:releng:googleplay:product:fenix": "fenix-repo",
                            "project:mobile:fenix:releng:signing:cert:nightly-signing": "fenix-repo",
                            "project:mobile:fenix:releng:signing:cert:beta-signing": "fenix-repo",
                            "project:mobile:fenix:releng:signing:cert:production-signing": "fenix-repo",
                            "project:mobile:fenix:releng:signing:cert:fennec-nightly-signing": "fenix-repo",
                            # Fennec Beta and Fennec Release share the same key
                            "project:mobile:fenix:releng:signing:cert:fennec-production-signing": "fenix-repo",
                            "project:mobile:fennec-profile-manager:releng:signing:cert:fennec-nightly-signing": "fennec-profile-manager-repo",
                            # Fennec Beta and Fennec Release share the same key
                            "project:mobile:fennec-profile-manager:releng:signing:cert:fennec-production-signing": "fennec-profile-manager-repo",
                            "project:mobile:firefox-tv:releng:googleplay:product:firefox-tv": "firefox-tv-repo",
                            "project:mobile:firefox-tv:releng:signing:cert:production-signing": "firefox-tv-repo",
                            "project:mobile:focus:googleplay:product:focus": "focus-repo",
                            "project:mobile:focus:releng:signing:cert:release-signing": "focus-repo",
                            "project:mobile:reference-browser:releng:googleplay:product:reference-browser": "reference-browser-repo",
                            "project:mobile:reference-browser:releng:signing:cert:release-signing": "reference-browser-repo",
                        }
                    ),
                    "mpd001": immutabledict(
                        {
                            "project:mpd001:releng:signing:cert:nightly-signing": "mpd001-repo",
                            "project:mpd001:releng:signing:cert:release-signing": "mpd001-repo",
                        }
                    ),
                    "application-services": immutabledict(
                        {"project:mozilla:application-services:releng:beetmover:bucket:maven-production": "application-services-repo"}
                    ),
                    "xpi": immutabledict({"project:xpi:signing:cert:release-signing": "xpi-manifest-repo"}),
                    "adhoc": immutabledict({"project:adhoc:signing:cert:release-signing": "adhoc-signing-repo"}),
                }
            )
        },
        # Map restricted-level to trees
        "cot_restricted_trees": {
            "by-cot-product": immutabledict(
                {
                    "firefox": immutabledict(
                        {
                            # Which repos can perform release actions?
                            # XXX remove /projects/maple and birch when taskcluster relpro
                            #     migration is tier1 and landed on mozilla-central
                            # XXX remove /projects/jamun when we no longer run staging releases
                            #     from it
                            "all-release-branches": (
                                "/releases/mozilla-beta",
                                "/releases/mozilla-release",
                                "/releases/mozilla-esr60",
                                "/releases/mozilla-esr68",
                                "/projects/birch",
                                "/projects/jamun",
                                "/projects/maple",
                            ),
                            # Limit things like pushapk to just these branches
                            "release": ("/releases/mozilla-release",),
                            "beta": ("/releases/mozilla-beta",),
                            "beta-or-release": ("/releases/mozilla-beta", "/releases/mozilla-release"),
                            "esr": ("/releases/mozilla-esr60", "/releases/mozilla-esr68"),
                            "esr68": ("/releases/mozilla-esr68",),
                            "nightly": ("/mozilla-central",),
                            # Which repos can do nightly signing?
                            # XXX remove /projects/maple and birch when taskcluster relpro
                            #     migration is tier1 and landed on mozilla-central
                            # XXX remove /projects/jamun when we no longer run staging releases
                            #     from it
                            # XXX remove /projects/oak when we no longer test updates against it
                            "all-nightly-branches": (
                                "/mozilla-central",
                                "/releases/mozilla-unified",
                                "/releases/mozilla-beta",
                                "/releases/mozilla-release",
                                "/releases/mozilla-esr60",
                                "/releases/mozilla-esr68",
                                "/projects/birch",
                                "/projects/jamun",
                                "/projects/oak",
                                "/projects/maple",
                            ),
                            "all-production-branches": (
                                "/mozilla-central",
                                "/releases/mozilla-beta",
                                "/releases/mozilla-release",
                                "/releases/mozilla-esr60",
                                "/releases/mozilla-esr68",
                            ),
                            "all-staging-branches": ("/projects/birch", "/projects/jamun", "/projects/maple"),
                        }
                    ),
                    "thunderbird": immutabledict(
                        {
                            "all-release-branches": ("/releases/comm-beta", "/releases/comm-esr60", "/releases/comm-esr68"),
                            "beta": ("/releases/comm-beta",),
                            "esr": ("/releases/comm-esr60", "/releases/comm-esr68"),
                            "all-nightly-branches": ("/comm-central", "/releases/comm-beta", "/releases/comm-esr60", "/releases/comm-esr68"),
                            "nightly": ("/comm-central",),
                        }
                    ),
                    "mobile": immutabledict(
                        {
                            "android-components-repo": ("/mozilla-mobile/android-components",),
                            "fenix-repo": ("/mozilla-mobile/fenix",),
                            "fennec-profile-manager-repo": ("/mozilla-mobile/fennec-profile-manager",),
                            "firefox-tv-repo": ("/mozilla-mobile/firefox-tv",),
                            "focus-repo": ("/mozilla-mobile/focus-android",),
                            "reference-browser-repo": ("/mozilla-mobile/reference-browser",),
                        }
                    ),
                    "mpd001": immutabledict({"mpd001-repo": ("/mozilla-services/guardian-vpn",)}),
                    "application-services": immutabledict({"application-services-repo": ("/mozilla/application-services",)}),
                    "xpi": immutabledict({"xpi-manifest-repo": ("/mozilla-extensions/xpi-manifest",)}),
                    "adhoc": immutabledict({"adhoc-signing-repo": ("/mozilla-releng/mvp-adhoc",)}),
                }
            )
        },
        "prebuilt_docker_image_task_types": {
            "by-cot-product": immutabledict(
                {
                    "firefox": ("decision", "action", "docker-image"),
                    "thunderbird": ("decision", "action", "docker-image"),
                    "mobile": "any",  # all allowed
                    "mpd001": "any",  # all allowed
                    "application-services": "any",  # all allowed
                    "xpi": "any",  # all allowed
                    "adhoc": "any",  # all allowed
                }
            )
        },
        "source_env_prefix": {
            "by-cot-product": immutabledict(
                {
                    "firefox": "GECKO",
                    "thunderbird": "COMM",
                    "mobile": "MOBILE",
                    "mpd001": "MPD001",
                    "application-services": "APPSERVICES",
                    "xpi": "XPI",
                    "adhoc": "ADHOC",
                }
            )
        },
    }
)


# get_reversed_statuses {{{1
def get_reversed_statuses(context: Any) -> Dict[int, str]:
    """Return a mapping of exit codes to status strings.

    Args:
        context (scriptworker.context.Context): the scriptworker context

    Returns:
        dict: the mapping of exit codes to status strings.

    """
    _rev = {v: k for k, v in STATUSES.items()}
    _rev.update(dict(context.config["reversed_statuses"]))
    return _rev
