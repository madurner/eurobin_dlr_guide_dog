if [ ! -f ./conan_env/conanrun.sh ]; then
    echo "conanrun.sh script not found. Install conan env...!"
    conan2 install conanfile.txt --output-folder conan_env --profile:host=$DLRRM_HOST_PLATFORM --profile:build=$DLRRM_HOST_PLATFORM --build=missing
fi

source conan_env/conanrun.sh
cd fast_api_backend/app/ || exit
python3 main.py
