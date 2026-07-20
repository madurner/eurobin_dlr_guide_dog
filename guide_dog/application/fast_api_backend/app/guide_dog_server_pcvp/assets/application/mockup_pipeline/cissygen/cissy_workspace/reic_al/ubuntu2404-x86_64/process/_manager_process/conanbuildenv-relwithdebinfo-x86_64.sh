script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/_manager_process"
echo "echo Restoring environment" > "$script_folder/deactivate_conanbuildenv-relwithdebinfo-x86_64.sh"
for v in NM RANLIB AR CPP CXX CC PYTHONPATH LN_MESSAGE_DEFINITION_DIRS
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
export PYTHONPATH="$PYTHONPATH:/volume/conan_cache/reic_al/.conan2/p/links229e186df6db1/p/lib/python/site-packages"
export LN_MESSAGE_DEFINITION_DIRS="$LN_MESSAGE_DEFINITION_DIRS:/volume/conan_cache/reic_al/.conan2/p/links593b0d3fea288/p/message_definitions"