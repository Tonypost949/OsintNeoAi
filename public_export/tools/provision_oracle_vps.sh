# Oracle Cloud Infrastructure (OCI) 4-vCPU 24GB RAM Always-Free Flex Config
export OCI_SHAPE="VM.Standard.A1.Flex"
export OCI_CPUS=4
export OCI_MEMORY_GB=24
export OCI_BOOT_VOLUME_GB=200
export OCI_IMAGE_OCID="canonical-ubuntu-24-04"

echo "[+] Oracle Cloud Always-Free VPS Provisioning Specs Ready:"
echo "    Shape: $OCI_SHAPE ($OCI_CPUS OCPUs, ${OCI_MEMORY_GB}GB RAM)"
echo "    Disk: ${OCI_BOOT_VOLUME_GB}GB"
