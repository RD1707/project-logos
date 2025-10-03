import { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Calendar, Edit2, Lock, Save, X } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Container from '../../components/layout/Container';
import Card, { CardBody, CardHeader } from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Badge from '../../components/ui/Badge';
import ErrorMessage from '../../components/ui/ErrorMessage';

export default function Perfil() {
  const { user, updateProfile, changePassword, loading } = useAuth();

  // Estado para edição de perfil
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    nome: user?.nome || '',
    bio: user?.bio || '',
    avatar_url: user?.avatar_url || ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Estado para mudança de senha
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [passwordData, setPasswordData] = useState({
    senhaAtual: '',
    senhaNova: '',
    senhaConfirmacao: ''
  });
  const [passwordError, setPasswordError] = useState('');

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    const result = await updateProfile(formData);

    if (result.success) {
      setSuccess('Perfil atualizado com sucesso!');
      setIsEditing(false);
      setTimeout(() => setSuccess(''), 3000);
    } else {
      setError(result.error || 'Erro ao atualizar perfil');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError('');

    if (passwordData.senhaNova !== passwordData.senhaConfirmacao) {
      setPasswordError('As senhas não coincidem');
      return;
    }

    if (passwordData.senhaNova.length < 6) {
      setPasswordError('A nova senha deve ter no mínimo 6 caracteres');
      return;
    }

    const result = await changePassword(
      passwordData.senhaAtual,
      passwordData.senhaNova
    );

    if (result.success) {
      // Usuário será redirecionado para login após troca de senha
    } else {
      setPasswordError(result.error || 'Erro ao alterar senha');
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
  };

  const getTipoLabel = (tipo) => {
    const tipos = {
      estudante: 'Estudante',
      professor: 'Professor',
      admin: 'Administrador'
    };
    return tipos[tipo] || tipo;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <Container size="md">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Meu Perfil</h1>
          <p className="mt-2 text-gray-600">
            Gerencie suas informações pessoais
          </p>
        </div>

        {/* Informações do Perfil */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Informações Pessoais
              </h2>
              {!isEditing && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit2 className="h-4 w-4 mr-2" />
                  Editar
                </Button>
              )}
            </div>
          </CardHeader>

          <CardBody>
            {success && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                {success}
              </div>
            )}

            {error && (
              <ErrorMessage title="Erro" message={error} />
            )}

            {!isEditing ? (
              // Modo visualização
              <div className="space-y-6">
                {/* Avatar e Nome */}
                <div className="flex items-center gap-6">
                  {user?.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.nome}
                      className="w-24 h-24 rounded-full object-cover border-4 border-gray-200"
                    />
                  ) : (
                    <div className="w-24 h-24 rounded-full bg-primary-600 text-white flex items-center justify-center text-3xl font-bold border-4 border-gray-200">
                      {user?.nome?.[0]?.toUpperCase()}
                    </div>
                  )}

                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{user?.nome}</h3>
                    <p className="text-gray-600">{user?.email}</p>
                    <div className="mt-2">
                      <Badge variant="default">
                        {getTipoLabel(user?.tipo)}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Bio */}
                {user?.bio && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Sobre
                    </label>
                    <p className="text-gray-600">{user.bio}</p>
                  </div>
                )}

                {/* Informações Adicionais */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-gray-200">
                  <div className="flex items-center gap-3 text-gray-600">
                    <Mail className="h-5 w-5" />
                    <div>
                      <div className="text-sm text-gray-500">Email</div>
                      <div className="font-medium">{user?.email}</div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 text-gray-600">
                    <Calendar className="h-5 w-5" />
                    <div>
                      <div className="text-sm text-gray-500">Membro desde</div>
                      <div className="font-medium">
                        {formatDate(user?.created_at)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              // Modo edição
              <form onSubmit={handleProfileUpdate} className="space-y-6">
                {/* Nome */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nome completo
                  </label>
                  <input
                    type="text"
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                {/* URL do Avatar */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    URL do Avatar (opcional)
                  </label>
                  <input
                    type="url"
                    value={formData.avatar_url}
                    onChange={(e) => setFormData({ ...formData, avatar_url: e.target.value })}
                    placeholder="https://exemplo.com/avatar.jpg"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sobre você (opcional)
                  </label>
                  <textarea
                    value={formData.bio}
                    onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                    rows={4}
                    placeholder="Conte um pouco sobre você..."
                    maxLength={500}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    {formData.bio?.length || 0}/500 caracteres
                  </p>
                </div>

                {/* Botões */}
                <div className="flex gap-3">
                  <Button type="submit" loading={loading}>
                    <Save className="h-4 w-4 mr-2" />
                    Salvar alterações
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      setIsEditing(false);
                      setFormData({
                        nome: user?.nome || '',
                        bio: user?.bio || '',
                        avatar_url: user?.avatar_url || ''
                      });
                      setError('');
                    }}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                </div>
              </form>
            )}
          </CardBody>
        </Card>

        {/* Alterar Senha */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">
                Segurança
              </h2>
            </div>
          </CardHeader>

          <CardBody>
            {!isChangingPassword ? (
              <div>
                <p className="text-gray-600 mb-4">
                  Mantenha sua conta segura alterando sua senha regularmente
                </p>
                <Button
                  variant="outline"
                  onClick={() => setIsChangingPassword(true)}
                >
                  <Lock className="h-4 w-4 mr-2" />
                  Alterar Senha
                </Button>
              </div>
            ) : (
              <form onSubmit={handlePasswordChange} className="space-y-4">
                {passwordError && (
                  <ErrorMessage title="Erro" message={passwordError} />
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Senha atual
                  </label>
                  <input
                    type="password"
                    value={passwordData.senhaAtual}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, senhaAtual: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nova senha
                  </label>
                  <input
                    type="password"
                    value={passwordData.senhaNova}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, senhaNova: e.target.value })
                    }
                    minLength={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmar nova senha
                  </label>
                  <input
                    type="password"
                    value={passwordData.senhaConfirmacao}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, senhaConfirmacao: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    required
                  />
                </div>

                <div className="flex gap-3">
                  <Button type="submit" loading={loading}>
                    <Save className="h-4 w-4 mr-2" />
                    Alterar Senha
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => {
                      setIsChangingPassword(false);
                      setPasswordData({
                        senhaAtual: '',
                        senhaNova: '',
                        senhaConfirmacao: ''
                      });
                      setPasswordError('');
                    }}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancelar
                  </Button>
                </div>
              </form>
            )}
          </CardBody>
        </Card>
      </Container>
    </div>
  );
}
