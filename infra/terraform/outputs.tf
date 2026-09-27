output "vpc_id" {
  description = "OpsPilot VPC ID."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs reserved for internet-facing load balancers."
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id,
  ]
}

output "private_subnet_ids" {
  description = "Private subnet IDs intended for EKS nodes and private resources."
  value = [
    aws_subnet.private_a.id,
    aws_subnet.private_b.id,
  ]
}

output "availability_zones" {
  description = "Availability Zones selected for the two-subnet-pair design."
  value = [
    aws_subnet.public_a.availability_zone,
    aws_subnet.public_b.availability_zone,
  ]
}

output "ecr_repository_url" {
  description = "Repository URL for OpsPilot container images."
  value       = aws_ecr_repository.opspilot.repository_url
}


output "eks_cluster_name" {
  description = "Amazon EKS cluster name."
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Amazon EKS API server endpoint."
  value       = aws_eks_cluster.main.endpoint
}

output "eks_node_group_name" {
  description = "Managed node group name."
  value       = aws_eks_node_group.main.node_group_name
}

output "nat_gateway_id" {
  description = "NAT Gateway used by private EKS nodes."
  value       = aws_nat_gateway.main.id
}
