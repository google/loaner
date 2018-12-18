# Description:
#   Bazel WORKSPACE for Grab n Go Loaner.

workspace(name = "gng")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "absl_archive",
    sha256 = "04bc3a5ccd72ef1de11486403905f75d3b1a2805a1ce0e4f4080df4075815e8e",
    strip_prefix = "abseil-py-fbaa5b3f56ba0c6feb7970738876213ed0da26aa",
    url = "https://github.com/abseil/abseil-py/archive/fbaa5b3f56ba0c6feb7970738876213ed0da26aa.tar.gz",
)

http_archive(
    name = "attr_archive",
    build_file = "//third_party:attr.BUILD",
    sha256 = "5d4d1b99f94d69338f485984127e4473b3ab9e20f43821b0e546cc3b2302fd11",
    strip_prefix = "attrs-17.2.0/src",
    urls = [
        "https://pypi.python.org/packages/be/41/e909cb6d901e9689da947419505cc7fb7d242a08a62ee221fce6a009a523/attrs-17.2.0.tar.gz",
    ],
)

http_archive(
    name = "beautifulsoup4_archive",
    build_file = "//third_party:beautifulsoup4.BUILD",
    sha256 = "b21ca09366fa596043578fd4188b052b46634d22059e68dd0077d9ee77e08a3e",
    strip_prefix = "beautifulsoup4-4.5.3",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/9b/a5/c6fa2d08e6c671103f9508816588e0fb9cec40444e8e72993f3d4c325936/beautifulsoup4-4.5.3.tar.gz",
        "https://pypi.python.org/packages/9b/a5/c6fa2d08e6c671103f9508816588e0fb9cec40444e8e72993f3d4c325936/beautifulsoup4-4.5.3.tar.gz",
    ],
)

http_archive(
    name = "cachetools_archive",
    build_file = "//third_party:cachetools.BUILD",
    sha256 = "d1a44ffd2eedd138f3ba69038feb807ea54cb24e8a207a52d3a8603bc4961821",
    strip_prefix = "cachetools-1.1.6",
    urls = [
        "https://pypi.python.org/packages/ba/00/b0ec69e21142cd838b2383a7881cf18368e35847cb66f908c8f25bcbaafc/cachetools-1.1.6.tar.gz",
    ],
)

http_archive(
    name = "certifi_archive",
    build_file = "//third_party:certifi.BUILD",
    sha256 = "a2d058239aa32def9bbe269bf6e095633c37af4903b38c0375c757804932a7a5",
    strip_prefix = "python-certifi-2017.11.05",
    urls = [
        "https://github.com/certifi/python-certifi/archive/2017.11.05.tar.gz",
    ],
)

http_archive(
    name = "chardet_archive",
    build_file = "//third_party:chardet.BUILD",
    sha256 = "d5620025cfca430f6c2e28ddbc87c3c66a5c82fa65570ae975c92911c2190189",
    strip_prefix = "chardet-3.0.4",
    urls = [
        "https://github.com/chardet/chardet/archive/3.0.4.tar.gz",
    ],
)

http_archive(
    name = "dateutil_archive",
    build_file = "//third_party:dateutil.BUILD",
    sha256 = "891c38b2a02f5bb1be3e4793866c8df49c7d19baabf9c1bad62547e0b4866aca",
    strip_prefix = "python-dateutil-2.6.1",
    urls = [
        "https://pypi.python.org/packages/54/bb/f1db86504f7a49e1d9b9301531181b00a1c7325dc85a29160ee3eaa73a54/python-dateutil-2.6.1.tar.gz",
    ],
)

http_archive(
    name = "dogpile_cache_archive",
    build_file = "//third_party:dogpile_cache.BUILD",
    sha256 = "a73aa3049cd88d7ec57a1c2e8946abdf4f14188d429c1023943fcc55c4568da1",
    strip_prefix = "dogpile.cache-0.6.4",
    urls = [
        "https://pypi.python.org/packages/b6/3d/35c05ca01c070bb70d9d422f2c4858ecb021b05b21af438fec5ccd7b945c/dogpile.cache-0.6.4.tar.gz",
    ],
)

http_archive(
    name = "endpoints_archive",
    build_file = "//third_party:endpoints.BUILD",
    sha256 = "b92b116037298fadb36a72e6bb4d0a68c5c5259afa1d1bcf95cfaaf252dc23a8",
    strip_prefix = "google-endpoints-4.0.0",
    urls = [
        "https://files.pythonhosted.org/packages/ac/2b/fc597f635dca86c6d28b85e9111830e926bae2fe34b9163d839ca29c8eee/google-endpoints-4.0.0.tar.gz",
    ],
)

http_archive(
    name = "enum_archive",
    build_file = "//third_party:enum.BUILD",
    sha256 = "8ad8c4783bf61ded74527bffb48ed9b54166685e4230386a9ed9b1279e2df5b1",
    strip_prefix = "enum34-1.1.6",
    urls = [
        "https://pypi.python.org/packages/bf/3e/31d502c25302814a7c2f1d3959d2a3b3f78e509002ba91aea64993936876/enum34-1.1.6.tar.gz",
    ],
)

http_archive(
    name = "fasteners_archive",
    build_file = "//third_party:fasteners.BUILD",
    sha256 = "427c76773fe036ddfa41e57d89086ea03111bbac57c55fc55f3006d027107e18",
    strip_prefix = "fasteners-0.14.1",
    urls = [
        "https://pypi.python.org/packages/f4/6f/41b835c9bf69b03615630f8a6f6d45dafbec95eb4e2bb816638f043552b2/fasteners-0.14.1.tar.gz",
    ],
)

http_archive(
    name = "freezegun_archive",
    build_file = "//third_party:freezegun.BUILD",
    sha256 = "783ccccd7f60968bfe49ad9e114c18ea2b63831faaaf61c1f1f71ddfde1c0eee",
    strip_prefix = "freezegun-0.3.9",
    urls = [
        "https://pypi.python.org/packages/89/f3/90fe43ea1261b763bdedb5e2e9ddc4f21c64cc439467113319430580978b/freezegun-0.3.9.tar.gz",
    ],
)

http_archive(
    name = "gapi_protos_archive",
    build_file = "//third_party:gapi_protos.BUILD",
    sha256 = "f94cc66efba677a086b8b17b1240239433495b77631cd410f70151a8ff14435d",
    strip_prefix = "googleapis-common-protos-1.5.2",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/96/6a/34759a4a2119a8aae0b19d045917ee4a39ffaaeda2df3a892730fdcda408/googleapis-common-protos-1.5.2.tar.gz",
        "https://pypi.python.org/packages/96/6a/34759a4a2119a8aae0b19d045917ee4a39ffaaeda2df3a892730fdcda408/googleapis-common-protos-1.5.2.tar.gz",
    ],
)

http_archive(
    name = "gcloud_api_core_archive",
    build_file = "//third_party:gcloud_api_core.BUILD",
    sha256 = "ac85fc7f6687bb0271f2f70ca298da90f35789f9de1fe3a11e8caeb571332b77",
    strip_prefix = "google-api-core-1.3.0",
    urls = [
        "https://files.pythonhosted.org/packages/85/e5/edfb19739e4aa98306b14a08ec5ab22f656631ad2d0c148367c69a3a8f82/google-api-core-1.3.0.tar.gz",
    ],
)

http_archive(
    name = "gcloud_auth_archive",
    build_file = "//third_party:gcloud_auth.BUILD",
    sha256 = "c12971320cf266ab1c7ed5a65ad311ad393695940f46315d05280207482e1eba",
    strip_prefix = "google-auth-library-python-1.3.0",
    urls = [
        "https://github.com/GoogleCloudPlatform/google-auth-library-python/archive/v1.3.0.tar.gz",
    ],
)

http_archive(
    name = "gcloud_bigquery_archive",
    build_file = "//third_party:gcloud_bigquery.BUILD",
    sha256 = "6e8cc6914701bbfd8845cc0e0b19c5e2123649fc6ddc49aa945d83629499f4ec",
    strip_prefix = "google-cloud-bigquery-0.25.0",
    urls = [
        "https://mirror.bazel.build/pypi.python.org/packages/4a/f1/05631b0a29b1f763794404195d161edb24d7463029c987e0a32fc521e2a6/google-cloud-bigquery-0.25.0.tar.gz",
        "https://pypi.python.org/packages/4a/f1/05631b0a29b1f763794404195d161edb24d7463029c987e0a32fc521e2a6/google-cloud-bigquery-0.25.0.tar.gz",
    ],
)

http_archive(
    name = "gcloud_core_archive",
    build_file = "//third_party:gcloud_core.BUILD",
    sha256 = "1249ee44c445f820eaf99d37904b37961347019dcd3637dbad1f3173260245f2",
    strip_prefix = "google-cloud-core-0.25.0",
    urls = [
        "https://mirror.bazel.build/pypi.python.org/packages/58/d0/c3a30eca2a0073d5ac00254a1a9d259929a899deee6e3dfe4e45264f5187/google-cloud-core-0.25.0.tar.gz",
        "https://pypi.python.org/packages/58/d0/c3a30eca2a0073d5ac00254a1a9d259929a899deee6e3dfe4e45264f5187/google-cloud-core-0.25.0.tar.gz",
    ],
)

http_archive(
    name = "gcloud_datastore_archive",
    build_file = "//third_party:gcloud_datastore.BUILD",
    sha256 = "d1f7e8d0a5f188e0d29b223e56bb3ea1ce129e60e00c448c1850dfb54fc5eaba",
    strip_prefix = "google-cloud-datastore-1.7.0",
    urls = [
        "https://files.pythonhosted.org/packages/fd/c2/98290b77dd5625720effeb6b3cf3930a7a8b757fddd6ef09cb2a1df4742c/google-cloud-datastore-1.7.0.tar.gz",
    ],
)

http_archive(
    name = "gcloud_resumable_media_archive",
    build_file = "//third_party:gcloud_resumable_media.BUILD",
    sha256 = "2d1a71cd2c4b8dae0005fa16d57c51969ce34d884a2ef1cd057e8c418a5a23c6",
    strip_prefix = "google-resumable-media-python-0.3.1",
    urls = [
        "https://github.com/GoogleCloudPlatform/google-resumable-media-python/archive/0.3.1.tar.gz",
    ],
)

http_archive(
    name = "gcloud_storage_archive",
    build_file = "//third_party:gcloud_storage.BUILD",
    sha256 = "c1969558df8d7994cf4f89f60c01c619d77fc19facb38f66640d1f749a663e2e",
    strip_prefix = "google-cloud-storage-1.10.0",
    urls = [
        "https://files.pythonhosted.org/packages/62/73/1ea71c8b319064bc6ae0530cb0f78fe15987c7881f132938e3fa83ddff46/google-cloud-storage-1.10.0.tar.gz",
    ],
)

http_archive(
    name = "googleapiclient_archive",
    build_file = "//third_party:googleapiclient.BUILD",
    sha256 = "4a807d2c6ea83186f0cb6ede00f42e0f4cf6daf01c4ec1e7e24863113527204d",
    strip_prefix = "google-api-python-client-1.6.4",
    urls = [
        "https://github.com/google/google-api-python-client/archive/v1.6.4.tar.gz",
    ],
)

http_archive(
    name = "google_apitools_archive",
    build_file = "//third_party:google_apitools.BUILD",
    sha256 = "4d838f73320ff1f038a73c0ac36b7419a226787e2738e15077311016b9fc6b7c",
    strip_prefix = "google-apitools-0.5.21",
    urls = [
        "https://pypi.python.org/packages/4d/28/11d3fd771290ad41e9df175e7ce33470b85a774129a24e7d58d38d7a6f3a/google-apitools-0.5.21.tar.gz",
    ],
)

http_archive(
    name = "google_auth_httplib2_archive",
    build_file = "//third_party:google_auth_httplib2.BUILD",
    sha256 = "098fade613c25b4527b2c08fa42d11f3c2037dda8995d86de0745228e965d445",
    strip_prefix = "google-auth-httplib2-0.0.3",
    urls = [
        "https://pypi.python.org/packages/e7/32/ac7f30b742276b4911a1439c5291abab1b797ccfd30bc923c5ad67892b13/google-auth-httplib2-0.0.3.tar.gz",
    ],
)

http_archive(
    name = "google_endpoints_api_management_archive",
    build_file = "//third_party:google_endpoints_api_management.BUILD",
    sha256 = "af7538542c0f521cea816e1487113d4494b461fee1e87e01efcfe4c1897817b6",
    strip_prefix = "google-endpoints-api-management-1.3.0",
    urls = [
        "https://pypi.python.org/packages/56/a8/0029f428e9f9e13d0dbda77276170aa5865dd021f0fe559304f68bdb93aa/google-endpoints-api-management-1.3.0.tar.gz",
    ],
)

http_archive(
    name = "html2text_archive",
    build_file = "//third_party:html2text.BUILD",
    sha256 = "02ab8df206e90a395b7e188e26eb1906680439ce4a636a00217851cef58c1fad",
    strip_prefix = "html2text-2017.10.4",
    urls = [
        "https://pypi.python.org/packages/dd/10/d257bb28d08b3e8a864ed28829508564cc4a864ba0a79fda42e4393f6842/html2text-2017.10.4.tar.gz",
    ],
)

http_archive(
    name = "httplib2_archive",
    build_file = "//third_party:httplib2.BUILD",
    sha256 = "e404d3b7bd86c1bc931906098e7c1305d6a3a6dcef141b8bb1059903abb3ceeb",
    strip_prefix = "httplib2-0.10.3/python2",
    urls = [
        "https://pypi.python.org/packages/e4/2e/a7e27d2c36076efeb8c0e519758968b20389adf57a9ce3af139891af2696/httplib2-0.10.3.tar.gz",
    ],
)

http_archive(
    name = "idna_archive",
    build_file = "//third_party:idna.BUILD",
    sha256 = "53c722c4b7908dfdf2e5db2b79982f1084494db7b34fd31ff6a296e9fddfceaa",
    strip_prefix = "idna-2.6",
    urls = [
        "https://github.com/kjd/idna/archive/v2.6.tar.gz",
    ],
)

http_archive(
     name = "io_bazel_rules_appengine",
     sha256 = "3cc3963d883c06d953181c28ce8c32ad4720779fca22a36891fc54ffb41c32d0",
     strip_prefix = "rules_appengine-edee76dd6892c1af75ad4166c1d3f709d240daf5",
     url = "https://github.com/bazelbuild/rules_appengine/archive/edee76dd6892c1af75ad4166c1d3f709d240daf5.tar.gz",
)

load(
    "@io_bazel_rules_appengine//appengine:py_appengine.bzl",
    "py_appengine_repositories"
)

py_appengine_repositories()

http_archive(
    name = "io_bazel_rules_python",
    sha256 = "8b32d2dbb0b0dca02e0410da81499eef8ff051dad167d6931a92579e3b2a1d48",
    strip_prefix = "rules_python-8b5d0683a7d878b28fffe464779c8a53659fc645",
    url = "https://github.com/bazelbuild/rules_python/archive/8b5d0683a7d878b28fffe464779c8a53659fc645.tar.gz",
)

load("@io_bazel_rules_python//python:pip.bzl", "pip_repositories", "pip_import")

pip_repositories()

pip_import(
    name = "pip_deps",
    requirements = "//third_party:requirements.txt",
)

load("@pip_deps//:requirements.bzl", "pip_install")

pip_install()

pip_import(
    name = "pip_grpcio",
    requirements = "//third_party:requirements.grpcio.txt",
)

load("@pip_grpcio//:requirements.bzl", pip_grpcio_install = "pip_install")

pip_grpcio_install()

http_archive(
    name = "mock_archive",
    build_file = "//third_party:mock.BUILD",
    sha256 = "b839dd2d9c117c701430c149956918a423a9863b48b09c90e30a6013e7d2f44f",
    strip_prefix = "mock-1.0.1",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/a2/52/7edcd94f0afb721a2d559a5b9aae8af4f8f2c79bc63fdbe8a8a6c9b23bbe/mock-1.0.1.tar.gz",
        "https://pypi.python.org/packages/a2/52/7edcd94f0afb721a2d559a5b9aae8af4f8f2c79bc63fdbe8a8a6c9b23bbe/mock-1.0.1.tar.gz",
    ],
)

http_archive(
    name = "monotonic_archive",
    build_file = "//third_party:monotonic.BUILD",
    sha256 = "a02611d5b518cd4051bf22d21bd0ae55b3a03f2d2993a19b6c90d9d168691f84",
    strip_prefix = "monotonic-1.4",
    urls = [
        "https://pypi.python.org/packages/14/73/04da85fc1bacfa94361f00205a464b7f1ed23bfe8de3511cbff0fa2eeda7/monotonic-1.4.tar.gz",
    ],
)
http_archive(
    name = "oauth2client_archive",
    build_file = "//third_party:oauth2client.BUILD",
    sha256 = "5b5b056ec6f2304e7920b632885bd157fa71d1a7f3ddd00a43b1541a8d1a2460",
    strip_prefix = "oauth2client-3.0.0",
    urls = [
        "https://pypi.python.org/packages/c0/7b/bc893e35d6ca46a72faa4b9eaac25c687ce60e1fbe978993fe2de1b0ff0d/oauth2client-3.0.0.tar.gz",
    ],
)

http_archive(
    name = "ply_archive",
    build_file = "//third_party:ply.BUILD",
    sha256 = "96e94af7dd7031d8d6dd6e2a8e0de593b511c211a86e28a9c9621c275ac8bacb",
    strip_prefix = "ply-3.10",
    urls = [
        "https://pypi.python.org/packages/ce/3d/1f9ca69192025046f02a02ffc61bfbac2731aab06325a218370fd93e18df/ply-3.10.tar.gz",
    ],
)

http_archive(
    name = "protobuf_archive",
    build_file = "//third_party:protobuf.BUILD",
    sha256 = "1489b376b0f364bcc6f89519718c057eb191d7ad6f1b395ffd93d1aa45587811",
    strip_prefix = "protobuf-3.6.1",
    urls = [
        "https://files.pythonhosted.org/packages/1b/90/f531329e628ff34aee79b0b9523196eb7b5b6b398f112bb0c03b24ab1973/protobuf-3.6.1.tar.gz",
    ],
)

http_archive(
    name = "pyasn1_archive",
    build_file = "//third_party:pyasn1.BUILD",
    sha256 = "8f646f3ec3028054da44a95d5fd6280e2e1af3319629c22626cf6a6514e1a576",
    strip_prefix = "pyasn1-0.4.2",
    urls = [
        "https://github.com/etingof/pyasn1/archive/v0.4.2.tar.gz",
    ],
)

http_archive(
    name = "pyasn1_modules_archive",
    build_file = "//third_party:pyasn1_modules.BUILD",
    sha256 = "fcd4b6d2d2ad3ca0ae1356a71e19a5e283d7e1141108206237bf0fc4bb349185",
    strip_prefix = "pyasn1-modules-0.2.1",
    urls = [
        "https://github.com/etingof/pyasn1-modules/archive/v0.2.1.tar.gz",
    ],
)

http_archive(
    name = "pyfakefs_archive",
    build_file = "//third_party:pyfakefs.BUILD",
    sha256 = "e5cf2cf734a06fa1e650a52fd0e0bf902b8f35ef984d5cbcdfbf25dfc7654677",
    strip_prefix = "pyfakefs-abf6cfd5754956d28f1dcbc6f8d21738d8dbfdc2",
    urls = [
        "https://github.com/jmcgeheeiv/pyfakefs/archive/abf6cfd5754956d28f1dcbc6f8d21738d8dbfdc2.tar.gz",
    ],
)

http_archive(
    name = "pyjwkest_archive",
    build_file = "//third_party:pyjwkest.BUILD",
    sha256 = "e8cf8d6f32245139e76c07021bb0f05c151f0136dfba631a9076b0f562c6b289",
    strip_prefix = "pyjwkest-1.0.1/src",
    urls = [
        "https://pypi.python.org/packages/64/72/275288499e91cfea8ad21fdda17c0c41d449da69c822cb0aa7ebc6a1ca0b/pyjwkest-1.0.1.tar.gz",
    ],
)

http_archive(
    name = "pylru_archive",
    build_file = "//third_party:pylru.BUILD",
    sha256 = "71376192671f0ad1690b2a7427d39a29b1df994c8469a9b46b03ed7e28c0172c",
    strip_prefix = "pylru-1.0.9",
    urls = [
        "https://pypi.python.org/packages/c0/7d/0de1055632f3871dfeaabe5a3f0510317cd98b93e7b792b44e4c7de2b17b/pylru-1.0.9.tar.gz",
    ],
)

http_archive(
    name = "pytz_archive",
    build_file = "//third_party:pytz.BUILD",
    sha256 = "ffb9ef1de172603304d9d2819af6f5ece76f2e85ec10692a524dd876e72bf277",
    strip_prefix = "pytz-2018.5",
    urls = [
        "https://files.pythonhosted.org/packages/ca/a9/62f96decb1e309d6300ebe7eee9acfd7bccaeedd693794437005b9067b44/pytz-2018.5.tar.gz",
    ],
)

http_archive(
    name = "requests_archive",
    build_file = "//third_party:requests.BUILD",
    sha256 = "b068ccce3b739a29cbf72148b0ff4be3d80198fb7cdbd63066f7384bb56ef917",
    strip_prefix = "requests-2.18.4",
    urls = [
        "https://github.com/requests/requests/archive/v2.18.4.tar.gz",
    ],
)

http_archive(
    name = "requests_toolbelt_archive",
    build_file = "//third_party:requests_toolbelt.BUILD",
    sha256 = "f6a531936c6fa4c6cfce1b9c10d5c4f498d16528d2a54a22ca00011205a187b5",
    strip_prefix = "requests-toolbelt-0.8.0",
    urls = [
        "https://pypi.python.org/packages/86/f9/e80fa23edca6c554f1994040064760c12b51daff54b55f9e379e899cd3d4/requests-toolbelt-0.8.0.tar.gz",
    ],
)

http_archive(
    name = "rsa_archive",
    build_file = "//third_party:rsa.BUILD",
    sha256 = "a25e4847ee24ec94af94ecd6a721f869be1136ffbc7df885dfd851dd6c948269",
    strip_prefix = "python-rsa-version-3.4.2",
    urls = [
        "https://github.com/sybrenstuvel/python-rsa/archive/version-3.4.2.tar.gz",
    ],
)

http_archive(
    name = "semver_archive",
    build_file = "//third_party:semver.BUILD",
    sha256 = "1ffb55fb86a076cf7c161e6b5931f7da59f15abe217e0f24cea96cc8eec50f42",
    strip_prefix = "semver-2.7.9",
    urls = [
        "https://files.pythonhosted.org/packages/40/56/d1f930872436300b474a447a8042091bd335119f0c58bd8647546d6c3dc0/semver-2.7.9.tar.gz",
    ],
)

http_archive(
    name = "setup_tools_archive",
    build_file = "//third_party:setup_tools.BUILD",
    sha256 = "6501fc32f505ec5b3ed36ec65ba48f1b975f52cf2ea101c7b73a08583fd12f75",
    strip_prefix = "setuptools-38.4.0",
    urls = [
        "https://pypi.python.org/packages/41/5f/6da80400340fd48ba4ae1c673be4dc3821ac06cd9821ea60f9c7d32a009f/setuptools-38.4.0.zip",
    ],
)

http_archive(
    name = "six_archive",
    build_file = "//third_party:six.BUILD",
    sha256 = "70e8a77beed4562e7f14fe23a786b54f6296e34344c23bc42f07b15018ff98e9",
    strip_prefix = "six-1.11.0",
    urls = [
        "https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz",
    ],
)

http_archive(
    name = "strict_rfc3339_archive",
    build_file = "//third_party:strict_rfc3339.BUILD",
    sha256 = "5cad17bedfc3af57b399db0fed32771f18fc54bbd917e85546088607ac5e1277",
    strip_prefix = "strict-rfc3339-0.7",
    urls = [
        "https://pypi.python.org/packages/56/e4/879ef1dbd6ddea1c77c0078cd59b503368b0456bcca7d063a870ca2119d3/strict-rfc3339-0.7.tar.gz",
    ],
)

http_archive(
    name = "uritemplate_archive",
    build_file = "//third_party:uritemplate.BUILD",
    sha256 = "c02643cebe23fc8adb5e6becffe201185bf06c40bda5c0b4028a93f1527d011d",
    strip_prefix = "uritemplate-3.0.0",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/cd/db/f7b98cdc3f81513fb25d3cbe2501d621882ee81150b745cdd1363278c10a/uritemplate-3.0.0.tar.gz",
        "https://pypi.python.org/packages/cd/db/f7b98cdc3f81513fb25d3cbe2501d621882ee81150b745cdd1363278c10a/uritemplate-3.0.0.tar.gz",
    ],
)

http_archive(
    name = "urllib3_archive",
    build_file = "//third_party:urllib3.BUILD",
    sha256 = "dd60d4104b871943e06be69e296e97ede9d42edf6ba534f0268aee932a601e2a",
    strip_prefix = "urllib3-1.22",
    urls = [
        "https://github.com/shazow/urllib3/archive/1.22.tar.gz",
    ],
)

http_archive(
    name = "waitress_archive",
    build_file = "//third_party:waitress.BUILD",
    sha256 = "c74fa1b92cb183d5a3684210b1bf0a0845fe8eb378fa816f17199111bbf7865f",
    strip_prefix = "waitress-1.0.2",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/cd/f4/400d00863afa1e03618e31fd7e2092479a71b8c9718b00eb1eeb603746c6/waitress-1.0.2.tar.gz",
        "https://pypi.python.org/packages/cd/f4/400d00863afa1e03618e31fd7e2092479a71b8c9718b00eb1eeb603746c6/waitress-1.0.2.tar.gz",
    ],
)

http_archive(
    name = "webtest_archive",
    build_file = "//third_party:webtest.BUILD",
    sha256 = "2b6abd2689f28a0b3575bcb5a36757f2344670dd13a8d9272d3a987c2fd1b615",
    strip_prefix = "WebTest-2.0.27",
    urls = [
        "http://mirror.bazel.build/pypi.python.org/packages/80/fa/ca3a759985c72e3a124cbca3e1f8a2e931a07ffd31fd45d8f7bf21cb95cf/WebTest-2.0.27.tar.gz",
        "https://pypi.python.org/packages/80/fa/ca3a759985c72e3a124cbca3e1f8a2e931a07ffd31fd45d8f7bf21cb95cf/WebTest-2.0.27.tar.gz",
    ],
)

http_archive(
    name = "yaml_archive",
    build_file = "//third_party:yaml.BUILD",
    sha256 = "592766c6303207a20efc445587778322d7f73b161bd994f227adaa341ba212ab",
    strip_prefix = "PyYAML-3.12/lib",
    urls = [
        "https://files.pythonhosted.org/packages/4a/85/db5a2df477072b2902b0eb892feb37d88ac635d36245a72a6a69b23b383a/PyYAML-3.12.tar.gz",
    ],
)
