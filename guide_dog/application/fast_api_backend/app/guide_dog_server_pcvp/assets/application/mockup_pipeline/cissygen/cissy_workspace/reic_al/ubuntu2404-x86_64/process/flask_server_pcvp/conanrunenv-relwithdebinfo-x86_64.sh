script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/flask_server_pcvp"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in CONAN_FLASK_PCVP_ROOT PYTHONPATH PATH CONAN_PCVP_CLIENT_PY_ROOT LD_LIBRARY_PATH DYLD_LIBRARY_PATH CONAN_PCVP_CLIENT_CPP_ROOT CONAN_PCVP_PROTOCOL_ROOT CONAN_TCLAP_ROOT CONAN_PCVP_COMMON_ROOT CONAN_PSTREAMS_ROOT CONAN_LOG4CXX_ROOT CONAN_PYBIND11_OPENCV_NUMPY_ROOT CONAN_FLASK_ROOT CONAN_ITSDANGEROUS_ROOT CONAN_WERKZEUG_ROOT
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

export CONAN_FLASK_PCVP_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/flask089085863b1b8/p"
export PYTHONPATH="$PYTHONPATH:/volume/conan_cache/reic_al/.conan2/p/werkz3437a2af7ed38/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/itsdaba157d9059f68/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/flask176d2c836e8b2/p/local/lib/python3.12/dist-packages:/volume/conan_cache/reic_al/.conan2/p/pcvp_eeaed569c9331/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/flask089085863b1b8/p/local/lib/python3.12/dist-packages"
export PATH="/volume/conan_cache/reic_al/.conan2/p/b/flask089085863b1b8/p/local/bin:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/bin:/volume/conan_cache/reic_al/.conan2/p/flask176d2c836e8b2/p/local/bin:$PATH"
export CONAN_PCVP_CLIENT_PY_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_eeaed569c9331/p"
export LD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/pcvp_eeaed569c9331/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$LD_LIBRARY_PATH:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib"
export DYLD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/pcvp_eeaed569c9331/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$DYLD_LIBRARY_PATH"
export CONAN_PCVP_CLIENT_CPP_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p"
export CONAN_PCVP_PROTOCOL_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p"
export CONAN_TCLAP_ROOT="/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p"
export CONAN_PCVP_COMMON_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p"
export CONAN_PSTREAMS_ROOT="/volume/conan_cache/reic_al/.conan2/p/pstre6b62fb282e173/p"
export CONAN_LOG4CXX_ROOT="/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p"
export CONAN_PYBIND11_OPENCV_NUMPY_ROOT="/volume/conan_cache/reic_al/.conan2/p/pybin846fb3f6916a8/p"
export CONAN_FLASK_ROOT="/volume/conan_cache/reic_al/.conan2/p/flask176d2c836e8b2/p"
export CONAN_ITSDANGEROUS_ROOT="/volume/conan_cache/reic_al/.conan2/p/itsdaba157d9059f68/p"
export CONAN_WERKZEUG_ROOT="/volume/conan_cache/reic_al/.conan2/p/werkz3437a2af7ed38/p"