script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/flask_server_pcvp"
echo "echo Restoring environment" > "$script_folder/deactivate_conanbuildenv-relwithdebinfo-x86_64.sh"
for v in NM RANLIB AR CPP CXX CC CMAKE_PREFIX_PATH PKG_CONFIG_LIBLOG4CXX_PREFIX PKG_CONFIG_PATH PKG_CONFIG_TCLAP_PREFIX
do
   is_defined="true"
   value=$(printenv $v) || is_defined="" || true
   if [ -n "$value" ] || [ -n "$is_defined" ]
   then
       echo export "$v='$value'" >> "$script_folder/deactivate_conanbuildenv-relwithdebinfo-x86_64.sh"
   else
       echo unset $v >> "$script_folder/deactivate_conanbuildenv-relwithdebinfo-x86_64.sh"
   fi
done

export NM="gcc-nm-13"
export RANLIB="gcc-ranlib-13"
export AR="gcc-ar-13"
export CPP="cpp-13"
export CXX="g++-13"
export CC="gcc-13"
export CMAKE_PREFIX_PATH="$CMAKE_PREFIX_PATH:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p:/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p/lib/cmake/pcvp_common:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/lib/cmake/pcvp_protocol:/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p/lib/cmake/pcvp_client_cpp"
export PKG_CONFIG_LIBLOG4CXX_PREFIX="/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p"
export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib/pkgconfig:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib/pkgconfig"
export PKG_CONFIG_TCLAP_PREFIX="/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p"