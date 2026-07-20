script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/pcvp_manager"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in CONAN_PCVP_MANAGER_ROOT PATH LD_LIBRARY_PATH DYLD_LIBRARY_PATH CONAN_PCVP_PROTOCOL_ROOT CONAN_TCLAP_ROOT CONAN_PCVP_COMMON_ROOT CONAN_PSTREAMS_ROOT CONAN_LOG4CXX_ROOT CONAN_PCVP_MANAGER_DEFINITIONS_ROOT
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

export CONAN_PCVP_MANAGER_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_01e3e821ee73b/p"
export PATH="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_01e3e821ee73b/p/bin:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_568182885b7da/p/bin:$PATH"
export LD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_01e3e821ee73b/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_568182885b7da/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_ec000a7eec457/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$LD_LIBRARY_PATH:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib"
export DYLD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_01e3e821ee73b/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/pcvp_568182885b7da/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_ec000a7eec457/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$DYLD_LIBRARY_PATH"
export CONAN_PCVP_PROTOCOL_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/pcvp_568182885b7da/p"
export CONAN_TCLAP_ROOT="/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p"
export CONAN_PCVP_COMMON_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_ec000a7eec457/p"
export CONAN_PSTREAMS_ROOT="/volume/conan_cache/reic_al/.conan2/p/pstre6b62fb282e173/p"
export CONAN_LOG4CXX_ROOT="/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p"
export CONAN_PCVP_MANAGER_DEFINITIONS_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_9420396fc6f09/p"