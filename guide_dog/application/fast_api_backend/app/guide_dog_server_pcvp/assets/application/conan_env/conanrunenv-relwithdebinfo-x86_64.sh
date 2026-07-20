script_folder="/home/reic_al/repositories/guide_dog/application/conan_env"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in CONAN_FASTAPI_ROOT PYTHONPATH PATH CONAN_ANNOTATED_DOC_ROOT CONAN_PYDANTIC_ROOT CONAN_ANNOTATED_TYPES_ROOT CONAN_PYDANTIC_CORE_ROOT CONAN_TYPING_INSPECTION_ROOT CONAN_TYPING_EXTENSIONS_ROOT CONAN_STARLETTE_ROOT CONAN_PCVP_CLIENT_PY_ROOT LD_LIBRARY_PATH DYLD_LIBRARY_PATH CONAN_PCVP_CLIENT_CPP_ROOT CONAN_PCVP_PROTOCOL_ROOT CONAN_TCLAP_ROOT CONAN_PCVP_COMMON_ROOT CONAN_PSTREAMS_ROOT CONAN_LOG4CXX_ROOT CONAN_PYBIND11_OPENCV_NUMPY_ROOT CONAN_OPENCV_PYTHON_ROOT CONAN_UVICORN_ROOT CONAN_PYTHON_MULTIPART_ROOT LN_MESSAGE_DEFINITION_DIRS CONAN_PRE_COMMIT_ROOT CONAN_CFGV_ROOT CONAN_IDENTIFY_ROOT CONAN_NODEENV_ROOT
do
   is_defined="true"
   value=$(printenv $v) || is_defined="" || true
   if [ -n "$value" ] || [ -n "$is_defined" ]
   then
       echo export "$v='$value'" >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
   else
       echo unset $v >> "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
   fi
done

export CONAN_FASTAPI_ROOT="/volume/conan_cache/reic_al/.conan2/p/fastab416102b6fa8b/p"
export PYTHONPATH="$PYTHONPATH:/volume/conan_cache/reic_al/.conan2/p/nodeede9ee9e52b739/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/identaaa61aea8ab77/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/cfgv1740e9e8b8ad5/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/pre-c52c17a2cb19b3/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib/python/site-packages:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib/python/site-packages:/volume/conan_cache/reic_al/.conan2/p/pytho24b5b451f3b8e/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/uvico10c9c1ed9e22c/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/opencf1da687316789/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_34a43be511991/p/lib:/volume/conan_cache/reic_al/.conan2/p/starl661e2b449cc0d/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/typin236bb6483492c/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/typinf1b6bfdab44cd/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/pydan9c213988f6b89/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/annot7b3d6cff505dc/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/pydan988612e1cb901/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/annot13acb0c86c6f7/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/fastab416102b6fa8b/p/local/lib/python3.12/dist-packages"
export PATH="/volume/conan_cache/reic_al/.conan2/p/fastab416102b6fa8b/p/local/bin:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_0e77121f88260/p/bin:/volume/conan_cache/reic_al/.conan2/p/uvico10c9c1ed9e22c/p/local/bin:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/bin:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/bin:/volume/conan_cache/reic_al/.conan2/p/pre-c52c17a2cb19b3/p/local/bin:/volume/conan_cache/reic_al/.conan2/p/identaaa61aea8ab77/p/local/bin:/volume/conan_cache/reic_al/.conan2/p/nodeede9ee9e52b739/p/local/bin:$PATH:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/bin:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/bin"
export CONAN_ANNOTATED_DOC_ROOT="/volume/conan_cache/reic_al/.conan2/p/annot13acb0c86c6f7/p"
export CONAN_PYDANTIC_ROOT="/volume/conan_cache/reic_al/.conan2/p/pydan988612e1cb901/p"
export CONAN_ANNOTATED_TYPES_ROOT="/volume/conan_cache/reic_al/.conan2/p/annot7b3d6cff505dc/p"
export CONAN_PYDANTIC_CORE_ROOT="/volume/conan_cache/reic_al/.conan2/p/pydan9c213988f6b89/p"
export CONAN_TYPING_INSPECTION_ROOT="/volume/conan_cache/reic_al/.conan2/p/typinf1b6bfdab44cd/p"
export CONAN_TYPING_EXTENSIONS_ROOT="/volume/conan_cache/reic_al/.conan2/p/typin236bb6483492c/p"
export CONAN_STARLETTE_ROOT="/volume/conan_cache/reic_al/.conan2/p/starl661e2b449cc0d/p"
export CONAN_PCVP_CLIENT_PY_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_34a43be511991/p"
export LD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_34a43be511991/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_d8e8d0cda7bdb/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_0e77121f88260/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_c921db20d74bf/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib:$LD_LIBRARY_PATH:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib"
export DYLD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_34a43be511991/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_d8e8d0cda7bdb/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_0e77121f88260/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_c921db20d74bf/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:/volume/conan_cache/reic_al/.conan2/p/links57c911f2f0e36/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib:$DYLD_LIBRARY_PATH"
export CONAN_PCVP_CLIENT_CPP_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_d8e8d0cda7bdb/p"
export CONAN_PCVP_PROTOCOL_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_0e77121f88260/p"
export CONAN_TCLAP_ROOT="/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p"
export CONAN_PCVP_COMMON_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_c921db20d74bf/p"
export CONAN_PSTREAMS_ROOT="/volume/conan_cache/reic_al/.conan2/p/pstre6b62fb282e173/p"
export CONAN_LOG4CXX_ROOT="/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p"
export CONAN_PYBIND11_OPENCV_NUMPY_ROOT="/volume/conan_cache/reic_al/.conan2/p/pybin846fb3f6916a8/p"
export CONAN_OPENCV_PYTHON_ROOT="/volume/conan_cache/reic_al/.conan2/p/opencf1da687316789/p"
export CONAN_UVICORN_ROOT="/volume/conan_cache/reic_al/.conan2/p/uvico10c9c1ed9e22c/p"
export CONAN_PYTHON_MULTIPART_ROOT="/volume/conan_cache/reic_al/.conan2/p/pytho24b5b451f3b8e/p"
export LN_MESSAGE_DEFINITION_DIRS="$LN_MESSAGE_DEFINITION_DIRS:/volume/conan_cache/reic_al/.conan2/p/links593b0d3fea288/p/message_definitions"
export CONAN_PRE_COMMIT_ROOT="/volume/conan_cache/reic_al/.conan2/p/pre-c52c17a2cb19b3/p"
export CONAN_CFGV_ROOT="/volume/conan_cache/reic_al/.conan2/p/cfgv1740e9e8b8ad5/p"
export CONAN_IDENTIFY_ROOT="/volume/conan_cache/reic_al/.conan2/p/identaaa61aea8ab77/p"
export CONAN_NODEENV_ROOT="/volume/conan_cache/reic_al/.conan2/p/nodeede9ee9e52b739/p"