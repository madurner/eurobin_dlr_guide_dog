script_folder="/home/reic_al/repositories/guide_dog/application/mockup_pipeline/cissygen/cissy_workspace/reic_al/ubuntu2404-x86_64/process/m3t_refiner_pcvp"
echo "echo Restoring environment" > "$script_folder/deactivate_conanrunenv-relwithdebinfo-x86_64.sh"
for v in CONAN_M3T_REFINER_CPP_PCVP_ROOT PATH LD_LIBRARY_PATH DYLD_LIBRARY_PATH CONAN_M3T_PCVP_ROOT CONAN_M3T_ROOT CONAN_COAL_ROOT CONAN_PCVP_CLIENT_CPP_ROOT CONAN_PCVP_PROTOCOL_ROOT CONAN_TCLAP_ROOT CONAN_PCVP_COMMON_ROOT CONAN_PSTREAMS_ROOT CONAN_LOG4CXX_ROOT
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

export CONAN_M3T_REFINER_CPP_PCVP_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/m3t_ra86fb44a3b65d/p"
export PATH="/volume/conan_cache/reic_al/.conan2/p/b/m3t_ra86fb44a3b65d/p/bin:/volume/conan_cache/reic_al/.conan2/p/b/m3t_p4ca6c4483c801/p/bin:/volume/conan_cache/reic_al/.conan2/p/m3tf289ac294140e/p/bin:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/bin:$PATH"
export LD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/m3t_ra86fb44a3b65d/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/m3t_p4ca6c4483c801/p/lib:/volume/conan_cache/reic_al/.conan2/p/m3tf289ac294140e/p/lib:/volume/conan_cache/reic_al/.conan2/p/coala4980b89a2889/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$LD_LIBRARY_PATH:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib"
export DYLD_LIBRARY_PATH="/volume/conan_cache/reic_al/.conan2/p/b/m3t_ra86fb44a3b65d/p/lib:/volume/conan_cache/reic_al/.conan2/p/b/m3t_p4ca6c4483c801/p/lib:/volume/conan_cache/reic_al/.conan2/p/m3tf289ac294140e/p/lib:/volume/conan_cache/reic_al/.conan2/p/coala4980b89a2889/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p/lib:/volume/conan_cache/reic_al/.conan2/p/liblib459dcf8618a3/p/lib:/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p/lib:/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p/lib:$DYLD_LIBRARY_PATH"
export CONAN_M3T_PCVP_ROOT="/volume/conan_cache/reic_al/.conan2/p/b/m3t_p4ca6c4483c801/p"
export CONAN_M3T_ROOT="/volume/conan_cache/reic_al/.conan2/p/m3tf289ac294140e/p"
export CONAN_COAL_ROOT="/volume/conan_cache/reic_al/.conan2/p/coala4980b89a2889/p"
export CONAN_PCVP_CLIENT_CPP_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_4dd8aed650c95/p"
export CONAN_PCVP_PROTOCOL_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_99ff97274e5a3/p"
export CONAN_TCLAP_ROOT="/volume/conan_cache/reic_al/.conan2/p/tclapf04bf9560c7f1/p"
export CONAN_PCVP_COMMON_ROOT="/volume/conan_cache/reic_al/.conan2/p/pcvp_bcb634da30b78/p"
export CONAN_PSTREAMS_ROOT="/volume/conan_cache/reic_al/.conan2/p/pstre6b62fb282e173/p"
export CONAN_LOG4CXX_ROOT="/volume/conan_cache/reic_al/.conan2/p/log4cb6e00c6f44d7b/p"