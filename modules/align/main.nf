
process BWA_INDEX {
  input:
  path file

  output:
  path "bwa", emit: index

  script:
  """
  mkdir bwa
  bwa index -p bwa/${file.baseName} $file
  """
}


process BWA_ALIGN {
  tag "$prefix"

  input:
  path ref
  path reads
  path index

  output:
  path '*.bam', emit: bam

  script:
  prefix = reads[0].getBaseName()
  """
  INDEX=`find -L ./ -name "*.amb" | sed 's/.amb//'`
  bwa mem \$INDEX $reads | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools sort | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools view -o ${prefix}.bam
  """
}

process BWA_ALIGN_PAIRED {
  tag "$prefix"

  input:
  path ref
  path reads1
  path reads2

  output: 
  path '*.bam', emit: bam

  script:
  prefix = ref[0].getBaseName()
  """
  bwa mem $ref $reads1 $reads2 | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools sort | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools view -o ${prefix}.bam
  """
}

process MINIMAP_INDEX {
  tag "$prefix"

  input:
  path ref

  output:
  path "*.mmi", emit: index

  script:
  """
  minimap2 -d "${ref.baseName}.mmi" $ref
  """
}

process MINIMAP {
  tag "$prefix"

  input:
  path ref
  path fasta
  path index

  output:
  path "*.bam", emit: bam

  script:
  """
  minimap2 -a --eqx $ref $fasta | samtools sort | samtools view -Sb > "${ref.baseName}.bam"
  """
}

process MINIMAP_PAIRED {
  tag "$prefix"

  input:
  path ref
  path fasta1
  path fasta2
  path index

  output:
  path "*.bam", emit: bam

  script:
  """
  minimap2 -ax sr --eqx $ref $fasta1 $fasta2 | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools view -Sb | /Users/mariatrofimova/Documents/samtools-1.14/bin/samtools sort -o "${ref.baseName}_sorted.bam"
  """
}
